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
	RUN dpkg --add-architecture amd64 \
	&& dpkg --add-architecture arm64 \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends ca-certificates curl libc6:amd64 libc6:arm64 make
	EOF

	podman build -q --iidfile "$tmpdir/image_id" "$tmpdir" > /dev/null
	image_id="$(<"$tmpdir/image_id")"
	
	cleanup
	exec podman run --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w /mnt "$image_id" /init "$@"
fi

arch="$1"
requirements="$2"
output="$3"

mkdir "$tmpdir/runtime"
curl -sSLf "https://github.com/astral-sh/python-build-standalone/releases/download/20250626/cpython-3.14.0b3%2B20250626-$arch-unknown-linux-gnu-install_only.tar.gz" | gzip -d | tar -x -C "$tmpdir/runtime" --strip-components 1

export PATH="$tmpdir/runtime/bin:$PATH"
pip install -q --root-user-action ignore --upgrade pip
pip install -q --root-user-action ignore -r "$requirements"
tar -c -C "$tmpdir/runtime" . | gzip > "$output"
