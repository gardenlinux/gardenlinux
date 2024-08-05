#!/bin/bash
set -o nounset
set -o errexit

SCRIPT_NAME="${0##*/}"
readonly SCRIPT_NAME

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
readonly SCRIPT_DIR

usage() {
    echo "Script to compare the apt repo version of two Garden Linux releases."
    echo "Usage: $SCRIPT_NAME VERSION_A VERSION_B"
    echo "Example: $SCRIPT_NAME 1443.10 1587.0"
    exit 1
}

main() {
    [[ $# -ge 2 ]] || usage
    [[ -n "$1" ]] || usage
    [[ -n "$2" ]] || usage
    local VERSION_A="${1}"; shift
    local VERSION_B="${1}"; shift

    TEMP_DIR=$(mktemp -d)

    trap 'rm -rf $TEMP_DIR' EXIT

    curl -s https://packages.gardenlinux.io/gardenlinux/dists/"$VERSION_A"/main/binary-amd64/Packages.gz | gunzip > "$TEMP_DIR"/"$VERSION_A"
    curl -s https://packages.gardenlinux.io/gardenlinux/dists/"$VERSION_B"/main/binary-amd64/Packages.gz | gunzip > "$TEMP_DIR"/"$VERSION_B"

    python3 "$SCRIPT_DIR"/parse-aptsource.py "$TEMP_DIR"/"$VERSION_A" > "$TEMP_DIR"/a
    python3 "$SCRIPT_DIR"/parse-aptsource.py "$TEMP_DIR"/"$VERSION_B" > "$TEMP_DIR"/b

    diff "$TEMP_DIR"/a "$TEMP_DIR"/b
}

main "${@}"

