#!/usr/bin/env python3
"""
Create a nightly failure issue manually by invoking the same
createNightlyFailureIssue() function used by the pipeline.

Requires: node, and @octokit/rest@21 installed in the repo root:
    npm install --no-save @octokit/rest@21

Usage:
    export GITHUB_TOKEN=ghp_...
    python3 hack/create_nightly_issue.py \\
        --repo gardenlinux/gardenlinux \\
        --run-id 12345678 \\
        --ref refs/heads/main \\
        --sha abc1234 \\
        [--workflow nightly] \\
        [--needs '{"build":{"result":"failure"},"test":{"result":"success"}}'] \\
        [--apt-compare-output "$(./hack/compare-apt-repo-versions.sh TODAY YESTERDAY)"] \\
        [--new-version 20240101] \\
        [--old-version 20231231]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).parent.parent / ".github" / "workflows"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, help="owner/repo, e.g. gardenlinux/gardenlinux")
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--ref", required=True, help="git ref, e.g. refs/heads/main")
    parser.add_argument("--sha", required=True, help="commit SHA")
    parser.add_argument("--workflow", default="nightly", help="workflow name (default: nightly)")
    parser.add_argument("--needs", default="{}", help="JSON object of needs context")
    parser.add_argument("--apt-compare-output", default="", help="stdout of compare-apt-repo-versions.sh")
    parser.add_argument("--new-version", default="", help="today's garden-version string")
    parser.add_argument("--old-version", default="", help="yesterday's garden-version string")
    parser.add_argument("--server-url", default="https://github.com")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    owner, repo = args.repo.split("/", 1)

    env = os.environ | {
        "GL_OWNER": owner,
        "GL_REPO": repo,
        "GL_RUN_ID": str(args.run_id),
        "GL_REF": args.ref,
        "GL_SHA": args.sha,
        "GL_WORKFLOW": args.workflow,
        "GL_SERVER_URL": args.server_url,
        "GL_NEEDS_JSON": args.needs,
        "GL_APT_COMPARE_OUTPUT": args.apt_compare_output,
        "GL_NEW_VERSION": args.new_version,
        "GL_OLD_VERSION": args.old_version,
    }

    runner = WORKFLOWS_DIR / "create_nightly_issue_runner.mjs"
    result = subprocess.run(["node", str(runner)], env=env)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
