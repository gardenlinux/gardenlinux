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


def create_nightly_failure_issue(
    session, owner, repo, run_id, ref, sha, workflow, needs, dry_run=False
):
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

    if dry_run:
        print(f"title: {title}\n")
        print(body)
        return

    resp = session.post(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        json={"title": title, "body": body},
    )
    resp.raise_for_status()
    issue = resp.json()
    print(f"Created issue: {issue['html_url']}")


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
