#!/usr/bin/env bash

set -eufo pipefail

tmpdir=

cleanup () {
	[ -n "$tmpdir" ] || rm -rf "$tmpdir"
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

	podman build --iidfile "$tmpdir/image_id" "$tmpdir"
	image_id="$(<"$tmpdir/image_id")"
	
	cleanup
	exec podman run --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w /mnt "$image_id" /init "$@"
fi

arch_host="$(uname -m)"
arch_target="$1"
requirements="$2"
output="$3"

# Download host architecture Python runtime for package installation
mkdir "$tmpdir/host_runtime"
curl -sSLf "https://github.com/astral-sh/python-build-standalone/releases/download/20250626/cpython-3.14.0b3%2B20250626-$arch_host-unknown-linux-gnu-install_only.tar.gz" | gzip -d | tar -x -C "$tmpdir/host_runtime" --strip-components 1

# Download target architecture Python runtime
mkdir "$tmpdir/runtime"
curl -sSLf "https://github.com/astral-sh/python-build-standalone/releases/download/20250626/cpython-3.14.0b3%2B20250626-$arch_target-unknown-linux-gnu-install_only.tar.gz" | gzip -d | tar -x -C "$tmpdir/runtime" --strip-components 1

# Use host Python to install packages into target runtime
export PATH="$tmpdir/host_runtime/bin:$PATH"
export PYTHONPATH="$tmpdir/runtime/lib/python3.14/site-packages"

# Create site-packages directory in target runtime
mkdir -p "$tmpdir/runtime/lib/python3.14/site-packages"

pip install \
    --only-binary=:all: \
    --target "$tmpdir/runtime/lib/python3.14/site-packages" \
    -r "$requirements"

# Create the final runtime archive
tar -c -C "$tmpdir/runtime" . | gzip >"$output"
