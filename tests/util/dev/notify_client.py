#!/usr/bin/env python3
"""
A simple filesystem monitor using watchfiles.

Usage:
    python notify_client.py -i /path/to/monitor -e /path/to/exclude --server HOST:PORT
"""

import argparse
import json
import os
import sys
import urllib.request

from watchfiles import Change, watch


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Monitor filesystem changes with watchfiles."
    )
    parser.add_argument(
        "-i",
        "--include",
        action="append",
        default=[],
        help="Path to add to monitoring (can be used multiple times).",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        default=[],
        help="Path to exclude from monitoring (can be used multiple times).",
    )
    parser.add_argument(
        "--server",
        help="HOST:PORT to send HTTP POST notifications to.",
    )
    return parser.parse_args()


def send_notification(server_url, path, event_type):
    """
    Send a JSON payload to the server via HTTP POST.
    """
    payload = json.dumps({"path": path, "event": event_type}).encode("utf-8")
    req = urllib.request.Request(
        server_url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Error sending notification: {e}", file=sys.stderr)


def main():
    args = parse_args()

    if not args.include:
        print("Error: At least one path must be specified with -i/--include.")
        sys.exit(1)

    includes = [os.path.abspath(p) for p in args.include]
    excludes = [os.path.abspath(p) for p in args.exclude]

    def changes_filter(change, path):
        if change == Change.deleted:
            return False
        if os.path.isdir(path):
            return False
        for ex in excludes:
            if path == ex or path.startswith(ex + os.sep):
                return False
        return True

    for path in includes:
        if not os.path.isdir(path):
            print(
                f"Error: Included path '{path}' is not a directory or does not exist."
            )
            sys.exit(1)

    server_url = None
    if args.server:
        server_url = f"http://{args.server}/"

    for changes in watch(*includes, watch_filter=changes_filter):
        for change, path in changes:
            if change == Change.added:
                event_type = "created"
            elif change == Change.modified:
                event_type = "modified"
            else:
                event_type = "unknown"

            if server_url:
                send_notification(server_url, path, event_type)


if __name__ == "__main__":
    main()
