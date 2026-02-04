#!/usr/bin/env python3
"""
Update Python version data in python.env.sh from upstream GitHub releases.

This script queries GitHub releases to find the latest Python runtime version
matching PYTHON_VERSION_SHORT and updates python.env.sh with new version,
release date, and checksums.
"""

import argparse
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict

from github import Github
from github.GithubException import GithubException

log = logging.getLogger(__name__)


def error(msg: str) -> None:
    """Log error and exit."""
    log.error(msg)
    sys.exit(1)


def parse_env_file(env_file: Path) -> Dict[str, str]:
    """Parse python.env.sh and extract environment variables."""
    if not env_file.exists():
        error(f"File not found: {env_file}")

    config = {}
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" in line:
                key, value = line.split("=", 1)
                config[key] = value.strip("\"'")
    return config


def get_latest_release(github: Github, repo_owner: str, repo_name: str):
    """Get the latest release from the repository."""
    start = time.time()
    log.debug(f"Getting repository {repo_owner}/{repo_name}...")
    repo = github.get_repo(f"{repo_owner}/{repo_name}")
    log.debug(f"Got repository in {time.time() - start:.2f}s")

    start = time.time()
    log.debug("Getting latest release...")
    release = repo.get_latest_release()
    log.debug(f"Got latest release {release.tag_name} in {time.time() - start:.2f}s")
    return release


def get_checksum_from_digest(asset) -> str:
    """Get checksum from asset digest."""
    log.debug(f"Getting checksum from digest for {asset.name}...")
    digest = getattr(asset, "digest", None) or asset.raw_data.get("digest", "")
    checksum = digest.replace("sha256:", "") if digest else ""
    if not re.match(r"^[0-9a-f]{64}$", checksum):
        error(f"Could not extract checksum for {asset.name}")
    return checksum


def extract_info(release, version_short: str) -> Dict[str, str]:
    """Extract all release information needed for python.env.sh."""
    tag_name = release.tag_name
    log.info(f"Checking release {tag_name} for Python {version_short}...")

    release_date_match = re.search(r"[0-9]{8}", tag_name)
    if not release_date_match:
        error(f"Could not extract release date from tag: {tag_name}")
        return {}  # Unreachable
    release_date = release_date_match.group(0)

    start = time.time()
    log.debug("Fetching assets ...")

    patterns = {
        "x86_64": re.compile(
            rf"cpython-{re.escape(version_short)}\.[0-9]+.*x86_64-unknown-linux-gnu.*install_only\.tar\.gz$"
        ),
        "aarch64": re.compile(
            rf"cpython-{re.escape(version_short)}\.[0-9]+.*aarch64-unknown-linux-gnu.*install_only\.tar\.gz$"
        ),
    }
    assets = {}

    for asset in release.get_assets():
        for arch, pattern in patterns.items():
            if arch not in assets and pattern.match(asset.name):
                assets[arch] = asset
                log.debug(f"Found {arch} asset: {asset.name}")

        if len(assets) == 2:
            log.debug("Found required assets, stopping iteration")
            break

    if "x86_64" not in assets:
        error(
            f"Latest release {tag_name} does not contain assets for Python version {version_short}"
        )
    if "aarch64" not in assets:
        error("Could not find aarch64 asset in release")

    python_version_match = re.search(
        r"cpython-([0-9]+\.[0-9]+\.[0-9]+)\+", assets["x86_64"].name
    )
    if not python_version_match:
        error(
            f"Could not extract PYTHON_VERSION from asset name: {assets['x86_64'].name}"
        )
        return {}  # Unreachable
    python_version = python_version_match.group(1)

    checksum_amd64 = get_checksum_from_digest(assets["x86_64"])
    checksum_arm64 = get_checksum_from_digest(assets["aarch64"])

    log.debug(f"Extracted all info in {time.time() - start:.2f}s")
    log.info(
        f"Found release: {tag_name}, PYTHON_VERSION: {python_version}, RELEASE_DATE: {release_date}"
    )

    return {
        "PYTHON_VERSION": python_version,
        "RELEASE_DATE": release_date,
        "PYTHON_ARCHIVE_CHECKSUM_AMD64": checksum_amd64,
        "PYTHON_ARCHIVE_CHECKSUM_ARM64": checksum_arm64,
    }


def update_file(env_file: Path, new_values: Dict[str, str]) -> bool:
    """Update python.env.sh with new values. Returns True if updated."""
    old_values = parse_env_file(env_file)

    with open(env_file, encoding="utf-8") as f:
        lines = f.readlines()

    updated = []
    for line in lines:
        matched = False
        for key in new_values:
            if re.match(rf"^export {key}=", line):
                updated.append(f'export {key}="{new_values[key]}"\n')
                matched = True
                break
        if not matched:
            updated.append(line)

    if updated == lines:
        log.info("No changes needed - file is already up to date")
        return False

    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(updated)
        log.info(f"Updated {env_file}")

        changes = [
            f"{k}: {old_values.get(k, '')} -> {new_values[k]}"
            for k in new_values
            if old_values.get(k, "") != new_values[k]
        ]
        if changes:
            log.info("Updated fields:")
            for change in changes:
                log.info(f"  {change}")
        return True
    except Exception as e:
        error(f"Failed to update file: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Update Python version data in python.env.sh"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    log.info("Starting Python runtime update...")

    env_file = Path(__file__).parent / "python.env.sh"
    config = parse_env_file(env_file)

    required_keys = ["PYTHON_VERSION_SHORT", "PYTHON_REPO_OWNER", "PYTHON_REPO_NAME"]
    for key in required_keys:
        if not config.get(key):
            error(f"Could not read {key} from python.env.sh")

    version_short = config["PYTHON_VERSION_SHORT"]
    repo = f"{config['PYTHON_REPO_OWNER']}/{config['PYTHON_REPO_NAME']}"
    log.info(f"Current PYTHON_VERSION_SHORT: {version_short}, Repository: {repo}")

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        error("GH_TOKEN or GITHUB_TOKEN environment variable is required")

    try:
        github = Github(token)
        log.info(f"Finding latest release matching Python {version_short}...")

        release = get_latest_release(
            github, config["PYTHON_REPO_OWNER"], config["PYTHON_REPO_NAME"]
        )
        new_values = extract_info(release, version_short)

        if update_file(env_file, new_values):
            log.info("Successfully updated Python version data")
    except GithubException as e:
        error(f"GitHub API error: {e}")
    except Exception as e:
        error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
