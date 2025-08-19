#!/usr/bin/env bash

set -eufo pipefail
set -x

tmpdir=

cleanup() {
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

if [ "$0" != /init ]; then
	cat >"$tmpdir/Containerfile" <<-'EOF'
		FROM debian:stable
		RUN apt-get update \
		&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl e2fsprogs qemu-utils gawk
	EOF

	podman build -q --iidfile "$tmpdir/image_id" "$tmpdir" >/dev/null
	image_id="$(<"$tmpdir/image_id")"

	cleanup
	exec podman run --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w /mnt "$image_id" /init "$@"
fi

tmpdir=

cleanup() {
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

input="$1"
output="$2"

mkdir "$tmpdir/dist"
gzip -d <"$input" | tar -x -C "$tmpdir/dist"

truncate -s 1G "$output"
mkfs.ext2 -q -d "$tmpdir/dist" -L GL_TESTS "$output"

# GCP does not support plain raw disks as images, so we need to create a tar.gz file that contains a file called disk.raw
tar -C "$(dirname "$output")" -czf "$(basename "$output").tar.gz" "$(basename "$output")"

# Azure needs a vhd file with specific parameters and with a specific aligned size
MB=$((1024 * 1024))
size=$(qemu-img info -f raw --output json "$output" | gawk 'match($0, /"virtual-size": ([0-9]+),/, val) {print val[1]}' | head -1)
rounded_size=$(((($size + $MB - 1) / $MB) * $MB))
qemu-img resize -f raw "$output" $rounded_size
qemu-img convert -f raw -O vpc -o subformat=fixed,force_size "$output" "${output/.raw/.vhd}"
