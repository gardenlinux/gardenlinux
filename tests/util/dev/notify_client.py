#!/usr/bin/env python3
"""
A simple filesystem monitor using watchdog.

Usage:
    python notify_client.py -i /path/to/monitor -e /path/to/exclude --server HOST:PORT
"""

import argparse
import json
import os
import sys
import urllib.request

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class MonitorHandler(FileSystemEventHandler):
    """
    Handles filesystem events and prints them unless the path is excluded.
    """

    def __init__(self, excludes, server_url=None):
        """
        :param excludes: List of absolute paths to exclude from monitoring.
        :param server_url: Optional URL to send HTTP POST notifications to.
        """
        super().__init__()
        self.excludes = [os.path.abspath(ex) for ex in excludes]
        self.server_url = server_url

    def _is_excluded(self, path):
        """
        Determine if the given path should be excluded.
        """
        abs_path = os.path.abspath(path)
        for ex in self.excludes:
            # Exclude if the path is the same as or inside the excluded path.
            if abs_path == ex or abs_path.startswith(ex + os.sep):
                return True
        return False

    def on_any_event(self, event):
        """
        Called on any filesystem event.
        """
        if event.event_type not in ["created", "deleted", "modified", "moved"]:
            return
        if event.is_directory:
            return
        if self._is_excluded(event.src_path):
            return
        print(f"[{event.event_type}] {event.src_path}")

        if self.server_url:
            payload = json.dumps(
                {"path": event.src_path, "event": event.event_type}
            ).encode("utf-8")
            req = urllib.request.Request(
                self.server_url,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            try:
                urllib.request.urlopen(req)
            except Exception as e:
                # Log the error but continue monitoring
                print(f"Error sending notification: {e}", file=sys.stderr)


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Monitor filesystem changes with watchdog."
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


def main():
    args = parse_args()

    if not args.include:
        print("Error: At least one path must be specified with -i/--include.")
        sys.exit(1)

    includes = [os.path.abspath(p) for p in args.include]
    excludes = [os.path.abspath(p) for p in args.exclude]

    for path in includes:
        if not os.path.isdir(path):
            print(
                f"Error: Included path '{path}' is not a directory or does not exist."
            )
            sys.exit(1)

    server_url = None
    if args.server:
        server_url = f"http://{args.server}/"

    event_handler = MonitorHandler(excludes, server_url)
    observer = Observer()

    for path in includes:
        observer.schedule(event_handler, path, recursive=True)

    observer.start()
    observer.join()


if __name__ == "__main__":
    main()
