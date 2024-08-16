#!/bin/bash
set -o errexit

SCRIPT_NAME="${0##*/}"
readonly SCRIPT_NAME

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
readonly SCRIPT_DIR

usage() {
    echo "Script to compare the apt repo version of Garden Linux with Debian."
    echo "Usage: $SCRIPT_NAME GL_VERSION"
    echo "Example: $SCRIPT_NAME 1599.0"
    exit 1
}

main() {
    [[ $# -ge 1 ]] || usage
    [[ -n "$1" ]] || usage
    local GL_VERSION="${1}"; shift

    TEMP_DIR=$(mktemp -d)

    trap 'rm -rf $TEMP_DIR' EXIT

    curl -s https://packages.gardenlinux.io/gardenlinux/dists/"$GL_VERSION"/main/binary-amd64/Packages.gz | gunzip > "$TEMP_DIR"/gardenlinux-"$GL_VERSION"
    curl -s https://deb.debian.org/debian/dists/testing/main/binary-amd64/Packages.gz | gunzip > "$TEMP_DIR"/debian-testing

    python3 "$SCRIPT_DIR"/parse-aptsource.py "$TEMP_DIR"/gardenlinux-"$GL_VERSION" > "$TEMP_DIR"/gardenlinux-"$GL_VERSION"-oneline
    python3 "$SCRIPT_DIR"/parse-aptsource.py "$TEMP_DIR"/debian-testing > "$TEMP_DIR"/debian-testing-oneline

    sort "$TEMP_DIR"/gardenlinux-"$GL_VERSION"-oneline | uniq > "$TEMP_DIR"/gardenlinux-"$GL_VERSION"-oneline-sorted
    sort "$TEMP_DIR"/debian-testing-oneline | uniq > "$TEMP_DIR"/debian-testing-oneline-sorted

    # Tested on macos, not sure if this works on linux too
    join -j 1 -o 0,1.2,2.2 "$TEMP_DIR"/gardenlinux-"$GL_VERSION"-oneline-sorted "$TEMP_DIR"/debian-testing-oneline-sorted | \
    awk '
    {
        # Remove gardenlinux suffix
        gsub(/gardenlinux[0-9]*$/, "", $2)
        gsub(/gardenlinux[0-9]*$/, "", $3)
        
        # Compare versions and print if different
        if ($2 != $3) {
            print $1 " " $2 " " $3
        }
    }'
}

main "${@}"

