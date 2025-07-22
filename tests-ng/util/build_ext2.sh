#!/usr/bin/env bash

set -eufo pipefail

if [ "$0" != /init ]; then
	exec podman run --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w /mnt debian:stable /init "$@"
fi

tmpdir=

cleanup () {
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

input="$1"
output="$2"

mkdir "$tmpdir/dist"
gzip -d < "$input" | tar -x -C "$tmpdir/dist"

truncate -s 1G "$output"
mkfs.ext2 -q -d "$tmpdir/dist" -L GL_TESTS "$output"
