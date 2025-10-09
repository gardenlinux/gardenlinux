#!/usr/bin/env python3
"""
Command-line interface for sysdiff functionality.
This is not bundled in the test-ng distribution but intended to be used for development purposes.
If the python dependencies are installed, it can be run from a developer's workstation.

Example Usage:
    tests-ng/util/sysdiff.py --name snapshot-name-1
    # change something
    tests-ng/util/sysdiff.py --name snapshot-name-2
    tests-ng/util/sysdiff.py --list
    tests-ng/util/sysdiff.py --diff snapshot-name-1 snapshot-name-2
    tests-ng/util/sysdiff.py --delete snapshot-name-1 snapshot-name-2

It can also be run containerized using the following command:

podman run -it --rm \
    -v $PWD:/mnt \
    ghcr.io/gardenlinux/nightly:nightly \
    bash -c "
        apt update;
        apt install -y python3-pip;
        pip install --break-system-packages -r /mnt/tests-ng/util/requirements.txt;
        bash"
/mnt/tests-ng/util/sysdiff.py
"""

import argparse
import sys
import os
from pathlib import Path

# Add tests-ng to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plugins.sysdiff import Sysdiff
from plugins.shell import ShellRunner


def list_snapshots(sysdiff: Sysdiff, verbose: bool = False):
    """List all available snapshots"""
    snapshots = sysdiff.manager.list_snapshots()

    if not snapshots:
        print("No snapshots found.")
        return

    print(f"Found {len(snapshots)} snapshot(s):")
    print()

    for snapshot_name in sorted(snapshots):
        try:
            snapshot = sysdiff.load_snapshot(snapshot_name)
            print(f"  {snapshot_name}")
            if verbose:
                print(f"    Created: {snapshot.metadata.created_at}")
                print(f"    Packages: {len(snapshot.packages)}")
                print(f"    Files: {len(snapshot.files)}")
                print(f"    Sysctl params: {len(snapshot.sysctl_params)}")
                print(f"    Kernel modules: {len(snapshot.kernel_modules)}")
                print(f"    Systemd units: {len(snapshot.systemd_units)}")
                print()
        except Exception as e:
            print(f"  {snapshot_name} (error loading: {e})")


def diff_snapshots(sysdiff: Sysdiff, snapshot1_name: str, snapshot2_name: str, verbose: bool = False):
    """Compare two snapshots and show differences"""
    try:
        print(f"Comparing snapshots:")
        print(f"  snapshot_a: {snapshot1_name}")
        print(f"  snapshot_b: {snapshot2_name}")
        print()

        diff_result = sysdiff.compare_snapshots(snapshot1_name, snapshot2_name)

        if not diff_result.has_changes:
            print("✓ No changes detected between snapshots")
            return

        print("✗ Changes detected:")
        print()

        diff_output = sysdiff.diff_engine.generate_diff(diff_result, snapshot1_name, snapshot2_name)
        print(diff_output)

    except Exception as e:
        print(f"✗ Error comparing snapshots: {e}")


def delete_snapshots(sysdiff: Sysdiff, snapshot_names: list, verbose: bool = False):
    """Delete specified snapshots"""
    if not snapshot_names:
        print("No snapshot names provided for deletion.")
        return

    available_snapshots = sysdiff.manager.list_snapshots()
    existing_snapshots = [name for name in snapshot_names if name in available_snapshots]
    missing_snapshots = [name for name in snapshot_names if name not in available_snapshots]

    if missing_snapshots:
        print(f"Warning: The following snapshots were not found: {', '.join(missing_snapshots)}")

    if not existing_snapshots:
        print("No existing snapshots to delete.")
        return

    if verbose:
        print(f"Deleting {len(existing_snapshots)} snapshot(s): {', '.join(existing_snapshots)}")

    try:
        sysdiff.cleanup_snapshots(existing_snapshots)
        print(f"✓ Successfully deleted {len(existing_snapshots)} snapshot(s)")
    except Exception as e:
        print(f"✗ Error deleting snapshots: {e}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Manage system snapshots for sysdiff comparison",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --name before-tests    # Create snapshot with name 'before-tests'
  %(prog)s --name after-tests     # Create snapshot with name 'after-tests'
  %(prog)s --list                 # List all snapshots
  %(prog)s --list --verbose       # List snapshots with details
  %(prog)s --delete snapshot-name # Delete specific snapshot
  %(prog)s --diff snapshot_a snapshot_b     # Compare two snapshots
  %(prog)s --diff snapshot_a snapshot_b -v  # Compare with detailed output
  %(prog)s --help                 # Show this help message
        """
    )

    # Create mutually exclusive group for main actions
    action_group = parser.add_mutually_exclusive_group(required=True)

    action_group.add_argument(
        "--name", "-n",
        type=str,
        help="Name for the snapshot (will be prefixed with timestamp)"
    )

    action_group.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available snapshots"
    )

    action_group.add_argument(
        "--delete", "-d",
        nargs="+",
        metavar="SNAPSHOT_NAME",
        help="Delete specified snapshot(s)"
    )

    action_group.add_argument(
        "--diff",
        nargs=2,
        metavar=("SNAPSHOT_A", "SNAPSHOT_B"),
        help="Compare two snapshots and show differences"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--paths",
        nargs="+",
        help="Custom paths to include in snapshot (default: /etc, /boot, /opt, /proc/mounts)"
    )

    parser.add_argument(
        "--ignore-file",
        type=str,
        help="Path to file containing ignore patterns"
    )

    args = parser.parse_args()

    try:
        shell = ShellRunner(None)
        sysdiff = Sysdiff(shell)

        if args.name:
            # Create snapshot
            snapshot = sysdiff.create_snapshot(
                name=args.name,
                paths=args.paths,
                ignore_file=Path(args.ignore_file) if args.ignore_file else None,
                verbose=args.verbose
            )

            print(f"✓ Snapshot created successfully: {snapshot.name}")
            print(f"  Location: {sysdiff.manager.state_dir / snapshot.name}.json.gz")
            print(f"  Packages: {len(snapshot.packages)}")
            print(f"  Files: {len(snapshot.files)}")
            print(f"  Sysctl params: {len(snapshot.sysctl_params)}")
            print(f"  Kernel modules: {len(snapshot.kernel_modules)}")
            print(f"  Systemd units: {len(snapshot.systemd_units)}")

            if args.verbose:
                print(f"\nDetailed information:")
                print(f"  Created at: {snapshot.metadata.created_at}")
                print(f"  Paths scanned: {snapshot.metadata.paths}")
                print(f"  Ignore file used: {snapshot.metadata.ignore_file}")

        elif args.list:
            list_snapshots(sysdiff, args.verbose)

        elif args.delete:
            delete_snapshots(sysdiff, args.delete, args.verbose)

        elif args.diff:
            snapshot_a_name, snapshot_b_name = args.diff
            diff_snapshots(sysdiff, snapshot_a_name, snapshot_b_name, args.verbose)

        return 0

    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        return 1

    except Exception as e:
        print(f"✗ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
