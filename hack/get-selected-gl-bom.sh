#!/bin/bash
set -o errexit

SCRIPT_NAME="${0##*/}"
readonly SCRIPT_NAME

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
readonly SCRIPT_DIR

usage() {
    echo "Get a list of important packages and their versions for a specific Garden Linux version."
    echo "Usage: $SCRIPT_NAME VERSION"
    echo "Example: $SCRIPT_NAME 1443.10"
    exit 1
}

main() {
    [[ $# -ge 1 ]] || usage
    [[ -n "$1" ]] || usage
    local VERSION="${1}"; shift

    TEMP_DIR=$(mktemp -d)

    trap 'rm -rf $TEMP_DIR' EXIT

    curl -s https://packages.gardenlinux.io/gardenlinux/dists/"$VERSION"/main/binary-amd64/Packages.gz | gunzip > "$TEMP_DIR"/"$VERSION"
    python3 "$SCRIPT_DIR"/parse-aptsource.py "$TEMP_DIR"/"$VERSION" > "$TEMP_DIR"/packages
    grep -E '^linux-image-amd64 |^systemd |^containerd |^runc |^curl |^openssl |^openssh-server |^libc-bin ' "$TEMP_DIR"/packages
}

main "${@}"
