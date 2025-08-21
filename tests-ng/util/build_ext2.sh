#!/usr/bin/env bash

set -eufo pipefail

tmpdir=

cleanup () {
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"


if [ "$0" != /init ]; then
	cat > "$tmpdir/Containerfile" <<-'EOF'
	FROM debian:stable
	RUN apt-get update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl e2fsprogs
	EOF

	podman build -q --iidfile "$tmpdir/image_id" "$tmpdir" > /dev/null
	image_id="$(<"$tmpdir/image_id")"
	
	cleanup
	exec podman run --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w /mnt "$image_id" /init "$@"
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
