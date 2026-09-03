#!/usr/bin/env python3
"""
Create a nightly failure issue by calling the GitHub REST API directly.

Usage:
    export GITHUB_TOKEN=ghp_...
    python3 hack/create_nightly_issue.py \\
        --repo gardenlinux/gardenlinux \\
        --run-id 12345678 \\
        [--ref refs/heads/main] \\
        [--sha abc1234] \\
        [--workflow nightly] \\
        [--needs '{"build":{"result":"failure"},"test":{"result":"success"}}']
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).parent.parent


def garden_version(date_str):
    result = subprocess.run(
        [REPO_ROOT / "bin" / "garden-version", date_str],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def apt_compare_output(new_version, old_version):
    script = REPO_ROOT / "hack" / "compare-apt-repo-versions.sh"
    result = subprocess.run(
        [script, new_version, old_version],
        capture_output=True,
        text=True,
    )
    return (
        result.stdout
        if result.returncode == 0
        else (
            result.stdout
            + result.stderr
            + f"\nFailed to run {script.name} {new_version} {old_version}"
        )
    )


def gh(session, path, **kwargs):
    resp = session.get(f"https://api.github.com{path}", **kwargs)
    resp.raise_for_status()
    return resp.json()


def get_last_job_log_lines(session, owner, repo, job_id):
    try:
        resp = session.get(
            f"https://api.github.com/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
            allow_redirects=True,
        )
        resp.raise_for_status()
        lines = [l for l in resp.text.splitlines() if l]
        last = lines[-10:] if lines else []
        return "\n".join(last) if last else "(no log output)"
    except Exception as e:
        return f"Error retrieving logs: {e}"


def find_quarterly_epic(session, owner, repo, logger):
    """
    Find the quarterly epic issue for the current quarter.
    Returns (issue_number, title) or (None, None).
    """
    try:
        dt = datetime.now(timezone.utc)
        year = dt.strftime("%y")  # two-digit year
        quarter = (dt.month - 1) // 3 + 1
        quarter_str = f"{year}Q{quarter}"
        search_title = f"Deliver nightly release candidates ({quarter_str})"
        logger.debug(f"Searching for quarterly epic: '{search_title}'")

        repo_name = f"{owner}/{repo}"
        resp = session.get(
            "https://api.github.com/search/issues",
            params={
                "q": f'"{search_title}" in:title repo:{repo_name} is:open is:issue',
                "per_page": 10,
            },
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        matches = [i for i in items if i["title"].strip() == search_title]
        if len(matches) == 1:
            logger.debug(f"Found epic: #{matches[0]['number']}")
            return matches[0]["number"], matches[0]["title"]
        elif len(matches) > 1:
            logger.warning(f"Multiple epics matched '{search_title}', omitting link.")
        else:
            logger.info(f"No open epic found for '{search_title}'.")
    except Exception as exc:
        logger.warning(f"Quarterly epic lookup failed: {exc}")
    return None, None


def find_existing_issue(session, owner, repo, run_id, logger):
    """
    Search for an existing issue that contains the dedup marker for this run.
    Returns a dict with 'number' and 'html_url', or None.
    """
    marker = f"nightly-issue: run_id={run_id}"
    repo_name = f"{owner}/{repo}"
    try:
        resp = session.get(
            "https://api.github.com/search/issues",
            params={
                "q": f'"{marker}" in:body repo:{repo_name} is:issue',
                "per_page": 5,
            },
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if items:
            logger.debug(f"Found existing issue #{items[0]['number']} for run {run_id}")
            return {"number": items[0]["number"], "html_url": items[0]["html_url"]}
    except Exception as exc:
        logger.warning(f"Dedup search failed: {exc}")
    return None


def add_sub_issue(session, owner, repo, epic_number, sub_issue_id, logger):
    """Register sub_issue_id as a sub-issue of epic_number."""
    try:
        resp = session.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{epic_number}/sub_issues",
            json={"sub_issue_id": sub_issue_id},
        )
        resp.raise_for_status()
        logger.debug(f"Linked issue id={sub_issue_id} as sub-issue of #{epic_number}")
    except Exception as exc:
        logger.warning(f"Sub-issue linking failed: {exc}")


def create_nightly_failure_issue(
    session, owner, repo, run_id, ref, sha, workflow, needs, dry_run=False, update=False
):
    logger = logging.getLogger(__name__)
    failed_needs = [
        (name, data) for name, data in needs.items() if data.get("result") == "failure"
    ]

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    title = f"Nightly workflow failed on {date} (run #{run_id})"
    run_url = f"https://github.com/{owner}/{repo}/actions/runs/{run_id}"

    body = "## Nightly workflow failed\n\n"
    body += f"A summary of the failure is provided below. See the [workflow run]({run_url}) for full details.\n\n"
    body += "| | |\n|---|---|\n"
    body += f"| **Workflow** | {workflow} |\n"
    body += f"| **Run** | {run_url} |\n"
    body += f"| **Ref** | {ref} |\n"
    body += f"| **SHA** | {sha} |\n\n"

    body += "### Failed jobs\n\n"
    if failed_needs:
        for name, data in failed_needs:
            body += f"- **{name}**: {data['result']}\n"
    else:
        body += "- No individual job reported a failure result, but the overall workflow failed.\n"

    jobs_data = (
        gh(session, f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs")
        if not dry_run
        else {"jobs": []}
    )
    failed_jobs = [
        j for j in jobs_data.get("jobs", []) if j.get("conclusion") == "failure"
    ]

    if failed_jobs:
        body += "\n### Failed job logs (last 10 lines)\n\n"
        for job in failed_jobs:
            log_lines = get_last_job_log_lines(session, owner, repo, job["id"])
            body += "<details>\n"
            body += f"<summary><b>{job['name']}</b></summary>\n\n"
            body += "```\n"
            body += log_lines
            body += "\n```\n\n"
            body += "</details>\n\n"

    if not dry_run:
        existing_issues = gh(
            session,
            f"/repos/{owner}/{repo}/issues",
            params={"state": "open", "per_page": 100},
        )
        duplicate = next(
            (i for i in existing_issues if f"run #{run_id}" in i.get("title", "")), None
        )
        if duplicate:
            print(f"NOTICE: Issue already exists for this run: {duplicate['html_url']}")
            return

    one_day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    merged_prs_url = (
        f"https://github.com/{owner}/{repo}/pulls"
        f"?q=is%3Apr+is%3Amerged+merged%3A%3E{one_day_ago}"
    )

    body += "\n### Pull requests merged in the last 24 hours\n\n"
    body += f"[View on GitHub]({merged_prs_url})\n"

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d")
    new_version = garden_version(today)
    old_version = garden_version(yesterday)
    compare_output = apt_compare_output(old_version, new_version)

    body += "\n### Apt packages updated since yesterday's nightly run\n\n"
    body += "<details>\n"
    body += "<summary>Click to expand</summary>\n\n"
    body += "```\n"
    body += compare_output or "(no output)"
    body += "\n```\n\n"
    body += "</details>\n\n"

    epic_number, epic_title = find_quarterly_epic(session, owner, repo, logger)
    if epic_number is not None:
        body += "\n### Quarterly epic\n\n"
        body += f"- #{epic_number} {epic_title}\n"

    labels = ["kind/epic", "theme/release-plan"]

    if dry_run:
        existing = find_existing_issue(session, owner, repo, run_id, logger)
        if existing:
            action = f"UPDATE #{existing['number']}" if update else f"SKIP (existing issue #{existing['number']})"
        else:
            action = "CREATE new issue"
        if epic_number is not None:
            print(f"Quarterly epic: #{epic_number} {epic_title}\n")
        else:
            print("Quarterly epic: none found\n")
        print(f"=== INTENDED ACTION ===\n{action}\n")
        if epic_number is not None:
            print(f"=== EPIC SUB-ISSUE ===\nWould link as sub-issue of #{epic_number}\n")
        else:
            print("=== EPIC SUB-ISSUE ===\nNo quarterly epic found\n")
        print(f"title: {title}\n")
        print(body)
        return

    existing = find_existing_issue(session, owner, repo, run_id, logger)

    if existing:
        if update:
            resp = session.patch(
                f"https://api.github.com/repos/{owner}/{repo}/issues/{existing['number']}",
                json={"title": title, "body": body, "labels": labels},
            )
            resp.raise_for_status()
            print(f"Updated issue: {existing['html_url']}")
            if epic_number is not None:
                add_sub_issue(session, owner, repo, epic_number, existing["id"], logger)
        else:
            print(f"NOTICE: Issue already exists for this run: {existing['html_url']}")
        return

    resp = session.post(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        json={"title": title, "body": body, "labels": labels},
    )
    resp.raise_for_status()
    issue = resp.json()
    print(f"Created issue: {issue['html_url']}")
    if epic_number is not None:
        add_sub_issue(session, owner, repo, epic_number, issue["id"], logger)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--repo", required=True, help="owner/repo, e.g. gardenlinux/gardenlinux"
    )
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--ref", default=None, help="git ref, e.g. refs/heads/main (default: current branch from git)")
    parser.add_argument("--sha", default=None, help="commit SHA (default: current HEAD from git)")
    parser.add_argument(
        "--workflow", default="nightly", help="workflow name (default: nightly)"
    )
    parser.add_argument("--needs", default="{}", help="JSON object of needs context")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the issue title and body without creating it",
    )
    args = parser.parse_args()

    if args.ref is None:
        result = subprocess.run(
            ["git", "-C", REPO_ROOT, "symbolic-ref", "HEAD"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            args.ref = result.stdout.strip()
        else:
            print("Error: --ref not supplied and could not determine ref from git.", file=sys.stderr)
            sys.exit(1)

    if args.sha is None:
        result = subprocess.run(
            ["git", "-C", REPO_ROOT, "rev-parse", "HEAD"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            args.sha = result.stdout.strip()
        else:
            print("Error: --sha not supplied and could not determine SHA from git.", file=sys.stderr)
            sys.exit(1)

    token = os.environ.get("GITHUB_TOKEN")
    if not token and not args.dry_run:
        print("Error: GITHUB_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    logging.basicConfig(
        level=logging.DEBUG if args.dry_run else logging.WARNING,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    try:
        needs = json.loads(args.needs)
    except json.JSONDecodeError as e:
        print(f"Error: --needs is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    owner, repo = args.repo.split("/", 1)

    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )

    create_nightly_failure_issue(
        session=session,
        owner=owner,
        repo=repo,
        run_id=args.run_id,
        ref=args.ref,
        sha=args.sha,
        workflow=args.workflow,
        needs=needs,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
