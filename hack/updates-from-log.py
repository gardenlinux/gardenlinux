#!/usr/bin/env python3
import argparse
import os
import re
import sys

# [2026-11-05 09:51:16] Get:1 https://packages.gardenlinux.io/gardenlinux 2410.0.0/main amd64 libcom-err2 amd64 1.47.4-1+b2 [19.5 kB]
rc_pkg_version = re.compile(r"Get:\d+ (?P<url>http\S+) (?P<release>\S+) (?P<arch>\S+) (?P<package>\S+) \S+ (?P<version>\S+)")
def fetch_package_versions_from_log(log_file, debug=False) -> tuple[dict, dict]:
    """
    Fetch the list of packages from the given build log file.

    Args:
        log_file (str): Path to the build log file.
        debug (bool): Enable debug output (default: False).

    Returns:
        tuple[dict, dict]: A tuple containing two dictionaries:
            - The first dictionary maps package names to their versions.
            - The second dictionary contains additional details for each package (url, release, arch).
    """
    packages = {}
    details = {}
    with open(log_file, "r") as f:
        for line in f:
            if "Get:" not in line:
                continue

            m = rc_pkg_version.search(line)
            if m:
                packages[m.group("package")] = m.group("version")
                if not details:
                    details = {
                        "url": m.group("url"),
                        "release": m.group("release"),
                        "gl_version": m.group("release").split("/")[0],
                        "arch": m.group("arch"),
                    }
                if debug:
                    print(f"DEBUG: {m.groupdict()} - {log_file}", file=sys.stderr)
    return packages, details

def changes_from_mirror(from_version: str, to_version: str, packages: set) -> dict:
    """
    calls "bash compare-apt-repo-version.sh {from_version} {to_version}" to fetch changes between two versions.
    processes lines of the form:
        -node-decamelize 4.0.0-2
        +node-decamelize 4.0.0-3
    
    Args:
        from_version (str): The starting version for comparison.
        to_version (str): The target version for comparison.
        packages (set): A set of package names to consider for changes.

    Returns:
        dict: a dictionary containing the changes between the two versions
    """
    os.chdir(os.path.dirname(__file__))
    import subprocess
    result = subprocess.run(
        ["bash", "compare-apt-repo-versions.sh", from_version, to_version],
        capture_output=True,
        text=True,
        check=True
    )

    print("NOTICE: From packages are pulled from mirror and may not have been in the image. Adds/Updates may be incorrect and removals are not supported for --from-version", file=sys.stderr)

    additions = {}
    removals = {}
    for line in result.stdout.splitlines():
        if line.startswith("-") and not line.startswith("---"):
            pkg, ver = line[1:].strip().split(' ', 1)
            removals[pkg] = {"from": ver, "to": None}
        elif line.startswith("+") and not line.startswith("+++"):
            pkg, ver = line[1:].strip().split(' ', 1)
            additions[pkg] = {"from": None, "to": ver}
    # updated: combine additions and removals into changes dictionary
    updated = {}
    for pkg, add in additions.copy().items():
        if pkg not in packages:
            del additions[pkg]
            continue

        if pkg in removals:
            updated[pkg] = {"from": removals[pkg]["from"], "to": add["to"]}
            del additions[pkg]
    return {"new": additions, "removed": {}, "updated": updated}


def diff_dicts(from_packages, to_packages) -> dict:
    changes = {"new": {}, "updated": {}, "removed": {}}
    for pkg, version in to_packages.items():
        from_version = from_packages.pop(pkg, None)
        if from_version is None:
            changes["new"][pkg] = {"from": None, "to": version}
        elif from_version != version:
            changes["updated"][pkg] = {"from": from_version, "to": version}
    for pkg, version in from_packages.items():
        changes["removed"][pkg] = {"from": version, "to": None}
    return changes

def output_text(changes: dict):
    for pkg, change in changes["new"].items():
        print(f"{pkg}: - -> {change['to']} (new)")
    for pkg, change in changes["updated"].items():
        print(f"{pkg}: {change['from']} -> {change['to']}")
    for pkg, change in changes["removed"].items():
        print(f"{pkg}: {change['from']} -> - (removed)")

class Colors:
    GREEN = "\033[32m"
    RED = "\033[31m"
    BOLD_RED = "\033[1;31m"
    ORANGE = "\033[38;5;208m"  # 256-color terminal
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    RESET = "\033[0m"
    GRAY = "\033[37m"

rc_version = re.compile(r"^v?(?P<epoch>\d+:)?(?P<version>\d+(?:\.\d+)*)(?P<build>-\d+)?(?P<suffix>[^\d].*)?$")
def color_versions(version_a: str, version_b: str) -> tuple[str, str]:
    colors = (Colors.BOLD_RED, Colors.GREEN, Colors.BLUE, Colors.RED, Colors.ORANGE, Colors.YELLOW)

    # the order of the version list is not the natural order of version components.
    # this is so that we can color the differing parts of the version correctly, without having to check the number of digits in the version
    def build_version_list(match):
        return [match.group("epoch") or ""] \
             + [match.group("build") or ""] \
             + [match.group("suffix") or ""] \
             + match.group("version").split(".")

    def color_diff(vers_a, vers_b):
        for i, (a, b) in enumerate(zip(vers_a, vers_b)):
            c = colors[i] if i < len(colors) else Colors.GREEN
            if a != b:
                vers_a[i] = f"{c}{a}{Colors.RESET}" if a else a
                vers_b[i] = f"{c}{b}{Colors.RESET}" if b else b
        return (
            vers_a[0] + ".".join(vers_a[3:]) + "".join(vers_a[1:3]),
            vers_b[0] + ".".join(vers_b[3:]) + "".join(vers_b[1:3])
        )

    match_a = rc_version.match(version_a)
    match_b = rc_version.match(version_b)
    version_a = build_version_list(match_a)
    version_b = build_version_list(match_b)
    return color_diff(version_a, version_b)

def output_color(changes: dict):
    for pkg, change in changes["new"].items():
        print(f"{pkg}: - -> {Colors.GREEN}{change['to']}{Colors.RESET} (new)")
    for pkg, change in changes["updated"].items():
        from_colored, to_colored = color_versions(change['from'], change['to'])
        print(f"{pkg}: {from_colored} -> {to_colored}")
    for pkg, change in changes["removed"].items():
        print(f": {Colors.GRAY}{pkg}{change['from']}{Colors.RESET} -> - (removed)")

def output_json(changes: dict):
    import json
    print(json.dumps(changes, indent=2))

formats = {
    "text": output_text,
    "json": output_json,
    "color": output_color,
}

def main():
    parser = argparse.ArgumentParser(description="Get a list of updated packages by log")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-log", "-f", help="Build log file")
    src.add_argument("--from-version", "-v", help="Build version")
    parser.add_argument("to_log", help="Build log file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug output")
    def_output = "color" if sys.stdout.isatty() else "text"
    parser.add_argument("--output", "-o", default=def_output, choices=formats.keys(), help="Output format (default: text or color if a tty is detected)")
    args = parser.parse_args()


    to_packages, details = fetch_package_versions_from_log(args.to_log, args.debug)

    if args.from_log:
        from_packages, _ = fetch_package_versions_from_log(args.from_log, args.debug)
        changes = diff_dicts(from_packages, to_packages)
        formats[args.output](changes)
    else:
        to_version = details.get("gl_version")
        changes = changes_from_mirror(args.from_version, to_version, set(to_packages.keys()))

        formats[args.output](changes)


if __name__ == "__main__":
    main()
