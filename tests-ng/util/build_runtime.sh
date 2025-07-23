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
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl
	EOF

	podman build -q --iidfile "$tmpdir/image_id" "$tmpdir" > /dev/null
	image_id="$(<"$tmpdir/image_id")"
	
	cleanup
	exec podman run --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w /mnt "$image_id" /init "$@"
fi

requirements="$1"
output="$2"

mkdir "$tmpdir/runtime"
mkdir "$tmpdir/site-packages"

for arch in x86_64 aarch64; do
	mkdir "$tmpdir/runtime/$arch"
	curl -sSLf "https://github.com/astral-sh/python-build-standalone/releases/download/20250626/cpython-3.14.0b3%2B20250626-$arch-unknown-linux-gnu-install_only.tar.gz" | gzip -d | tar -x -C "$tmpdir/runtime/$arch" --strip-components 1
	if [ ! -e "$tmpdir/runtime/site-packages" ]; then
		mv "$tmpdir/runtime/$arch/lib/python3.14/site-packages" "$tmpdir/runtime/site-packages"
	else
		rm -rf "$tmpdir/runtime/$arch/lib/python3.14/site-packages"
	fi
	ln -s ../../../site-packages "$tmpdir/runtime/$arch/lib/python3.14/site-packages"
done

export PATH="$tmpdir/runtime/$(uname -m)/bin:$PATH"
pip install -q --root-user-action ignore --disable-pip-version-check --only-binary=:none: -r "$requirements"
tar -c -C "$tmpdir/runtime" . | gzip > "$output"
