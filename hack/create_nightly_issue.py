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
import io
import json
import logging
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree

import requests

REPO_ROOT = Path(__file__).parent.parent

# Maximum failed/errored testcase lines to include in the issue body.
MAX_FAILED_TESTS = 100

# GitHub issue body character limit.
GITHUB_BODY_LIMIT = 65536


def get_test_report_artifact(session, owner, repo, run_id, logger):
    """
    Find the newest non-expired test-report artifact for the run.
    Returns (artifact_id, artifact_name) or (None, None).
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts?per_page=100"
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    artifacts = resp.json().get("artifacts", [])

    candidates = [
        a for a in artifacts
        if a["name"] == "test-report" and not a.get("expired", False)
    ]
    if not candidates:
        logger.info("No non-expired 'test-report' artifact found for this run.")
        return None, None

    # Pick newest by created_at
    candidates.sort(key=lambda a: a["created_at"], reverse=True)
    chosen = candidates[0]
    logger.debug(f"Using test-report artifact id={chosen['id']} created={chosen['created_at']}")
    return chosen["id"], chosen["name"]


def download_artifact_zip(session, owner, repo, artifact_id, logger):
    """Download artifact zip; returns raw bytes or None on error."""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip"
    resp = session.get(url, timeout=120, allow_redirects=True)
    if resp.status_code == 410:
        logger.warning("Artifact download returned 410 Gone (expired after listing).")
        return None
    resp.raise_for_status()
    return resp.content


def parse_junit_xml(xml_bytes, source_name):
    """
    Parse a junit XML file. Returns a dict:
      {tests, failures, errors, skipped, failed_cases: [{name, classname, message}]}
    """
    result = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "failed_cases": []}
    try:
        root = ElementTree.fromstring(xml_bytes)
    except ElementTree.ParseError:
        return result

    # Handle both <testsuites><testsuite> and bare <testsuite>
    if root.tag == "testsuites":
        suites = list(root.iter("testsuite"))
    elif root.tag == "testsuite":
        suites = list(root.iter("testsuite"))
    else:
        suites = list(root.iter("testsuite"))

    # Aggregate at testcase level to avoid double-counting nested suites
    seen_cases = set()
    for suite in suites:
        for tc in suite.findall("testcase"):
            # Build unique key to avoid double-counting
            tc_name = tc.get("name", "")
            tc_class = tc.get("classname", "")
            tc_time = tc.get("time", "")
            key = (tc_class, tc_name, tc_time)
            if key in seen_cases:
                continue
            seen_cases.add(key)
            result["tests"] += 1

            failure = tc.find("failure")
            error = tc.find("error")
            skipped = tc.find("skipped")

            if skipped is not None:
                result["skipped"] += 1
            elif failure is not None:
                result["failures"] += 1
                msg = (failure.get("message") or failure.text or "").strip()
                msg = msg[:200] if len(msg) > 200 else msg
                result["failed_cases"].append({
                    "name": tc_name,
                    "classname": tc_class,
                    "message": msg,
                    "source": source_name,
                    "kind": "failure",
                })
            elif error is not None:
                result["errors"] += 1
                msg = (error.get("message") or error.text or "").strip()
                msg = msg[:200] if len(msg) > 200 else msg
                result["failed_cases"].append({
                    "name": tc_name,
                    "classname": tc_class,
                    "message": msg,
                    "source": source_name,
                    "kind": "error",
                })

    return result


def parse_test_report_zip(zip_bytes, logger):
    """
    Parse all *.test.xml files in the artifact zip.
    Returns aggregated totals and list of all failed/errored cases.
    """
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    all_failed = []

    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        logger.warning("Downloaded artifact is not a valid zip file.")
        return totals, all_failed

    xml_members = [m for m in zf.namelist() if m.endswith(".test.xml")]
    logger.debug(f"Found {len(xml_members)} *.test.xml files in artifact")

    for member in xml_members:
        source_name = member.split("/")[-1].replace(".test.xml", "")
        try:
            xml_bytes = zf.read(member)
        except Exception as exc:
            logger.warning(f"Could not read {member}: {exc}")
            continue
        parsed = parse_junit_xml(xml_bytes, source_name)
        totals["tests"] += parsed["tests"]
        totals["failures"] += parsed["failures"]
        totals["errors"] += parsed["errors"]
        totals["skipped"] += parsed["skipped"]
        all_failed.extend(parsed["failed_cases"])

    return totals, all_failed


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
    Search for an existing issue whose title contains the run ID.
    Returns a dict with 'number', 'id', and 'html_url', or None.
    """
    repo_name = f"{owner}/{repo}"
    query = f'"run #{run_id}" in:title repo:{repo_name} is:issue'
    try:
        resp = session.get(
            "https://api.github.com/search/issues",
            params={"q": query, "per_page": 5},
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if items:
            logger.debug(f"Found existing issue #{items[0]['number']} for run {run_id}")
            return {
                "number": items[0]["number"],
                "id": items[0]["id"],
                "html_url": items[0]["html_url"],
            }
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

    # --- Phase A: collect all data (runs once) ---

    all_jobs = []
    page = 1
    while True:
        jobs_data = gh(
            session,
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs?per_page=100&page={page}",
        )
        batch = jobs_data.get("jobs", [])
        all_jobs.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    logger.debug(f"Fetched {len(all_jobs)} jobs for run {run_id}")
    failed_jobs = [j for j in all_jobs if j.get("conclusion") == "failure"]

    # Fetch job logs once and cache them
    log_lines_map = {}
    for job in failed_jobs:
        log_lines_map[job["id"]] = get_last_job_log_lines(session, owner, repo, job["id"])

    # Test results from test-report artifact
    test_totals = None
    all_failed = []
    logger.info("Looking for test-report artifact ...")
    artifact_id, _ = get_test_report_artifact(session, owner, repo, run_id, logger)
    if artifact_id:
        logger.info(f"Downloading artifact {artifact_id} ...")
        try:
            zip_bytes = download_artifact_zip(session, owner, repo, artifact_id, logger)
            if zip_bytes:
                logger.info("Parsing junit XML from artifact ...")
                test_totals, all_failed = parse_test_report_zip(zip_bytes, logger)
                logger.info(
                    f"Test results: {test_totals['tests']} tests, "
                    f"{test_totals['failures']} failures, "
                    f"{test_totals['errors']} errors, "
                    f"{test_totals['skipped']} skipped"
                )
        except Exception as exc:
            logger.warning(f"Test report processing failed: {exc}")

    one_day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    merged_prs_url = (
        f"https://github.com/{owner}/{repo}/pulls"
        f"?q=is%3Apr+is%3Amerged+merged%3A%3E{one_day_ago}"
    )

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d")
    new_version = garden_version(today)
    old_version = garden_version(yesterday)
    compare_output = apt_compare_output(old_version, new_version)

    epic_number, epic_title = find_quarterly_epic(session, owner, repo, logger)

    # --- Phase B: render body (may run multiple times to fit within limit) ---

    def _render_body(failed_test_limit):
        b = "## Nightly workflow failed\n\n"
        b += f"A summary of the failure is provided below. See the [workflow run]({run_url}) for full details.\n\n"
        b += "| | |\n|---|---|\n"
        b += f"| **Workflow** | {workflow} |\n"
        b += f"| **Run** | {run_url} |\n"
        b += f"| **Ref** | {ref} |\n"
        b += f"| **SHA** | {sha} |\n\n"

        b += "### Failed jobs\n\n"
        if failed_needs:
            for name, data in failed_needs:
                b += f"- **{name}**: {data['result']}\n"
        elif failed_jobs:
            for job in failed_jobs:
                job_name = job.get("name", "unknown")
                job_url = job.get("html_url", "")
                job_conclusion = job.get("conclusion", "unknown")
                if job_url:
                    b += f"- [{job_name}]({job_url}) — `{job_conclusion}`\n"
                else:
                    b += f"- {job_name} — `{job_conclusion}`\n"
        else:
            b += "- No failed jobs detected.\n"

        if failed_jobs:
            b += "\n### Failed job logs (last 10 lines)\n\n"
            for job in failed_jobs:
                log_lines = log_lines_map.get(job["id"], "(no log output)")
                b += "<details>\n"
                b += f"<summary><b>{job['name']}</b></summary>\n\n"
                b += "```\n"
                b += log_lines
                b += "\n```\n\n"
                b += "</details>\n\n"

        b += "\n## Test results\n\n"
        if test_totals is None:
            b += "_Test report artifact was not found or has expired._\n\n"
        else:
            passed = (
                test_totals["tests"]
                - test_totals["failures"]
                - test_totals["errors"]
                - test_totals["skipped"]
            )
            b += "| Total | Passed | Failed | Errors | Skipped |\n"
            b += "|---|---|---|---|---|\n"
            b += (
                f"| {test_totals['tests']} | {passed} | {test_totals['failures']} "
                f"| {test_totals['errors']} | {test_totals['skipped']} |\n\n"
            )

            if all_failed:
                effective_limit = max(0, failed_test_limit)
                truncated = all_failed[:effective_limit]
                b += "<details>\n"
                b += f"<summary>Failed/errored test cases ({len(all_failed)} total)</summary>\n\n"
                for tc in truncated:
                    source = tc.get("source", "")
                    classname = tc.get("classname", "")
                    name = tc.get("name", "")
                    msg = tc.get("message", "").replace("\n", " ").replace("|", "\\|")
                    test_id = f"{classname}::{name}" if classname else name
                    b += f"- **`{source}`** `{test_id}`: {msg}\n"
                if len(all_failed) > effective_limit:
                    b += f"\n_... and {len(all_failed) - effective_limit} more (truncated)._\n"
                b += "\n</details>\n\n"

        b += "\n### Pull requests merged in the last 24 hours\n\n"
        b += f"[View on GitHub]({merged_prs_url})\n"

        b += "\n### Apt packages updated since yesterday's nightly run\n\n"
        b += "<details>\n"
        b += "<summary>Click to expand</summary>\n\n"
        b += "```\n"
        b += compare_output or "(no output)"
        b += "\n```\n\n"
        b += "</details>\n\n"

        if epic_number is not None:
            b += "\n### Quarterly epic\n\n"
            b += f"- #{epic_number} {epic_title}\n"

        return b

    # Render and trim until within GitHub's body limit
    limit = MAX_FAILED_TESTS
    body = _render_body(limit)
    while len(body) > GITHUB_BODY_LIMIT and limit > 0:
        limit = max(0, limit - 10)
        logger.warning(
            f"Issue body exceeds {GITHUB_BODY_LIMIT} chars; "
            f"reducing failed test cases to {limit}"
        )
        body = _render_body(limit)
    if len(body) > GITHUB_BODY_LIMIT:
        logger.warning(
            f"Issue body still exceeds {GITHUB_BODY_LIMIT} chars ({len(body)}) "
            "after reducing failed test cases to 0; proceeding anyway"
        )
    logger.info(f"Final issue body length: {len(body)} chars")

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
    parser.add_argument(
        "--update",
        action="store_true",
        help="update an existing issue for this run instead of skipping",
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
    if not token:
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
        update=args.update,
    )


if __name__ == "__main__":
    main()
