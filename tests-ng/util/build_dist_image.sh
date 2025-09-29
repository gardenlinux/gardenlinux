#!/usr/bin/env bash

set -euxfo pipefail

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
		&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl e2fsprogs qemu-utils gawk retry
	EOF

	podman build --iidfile "$tmpdir/image_id" "$tmpdir" # >/dev/null
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

qemu-img create "$output" 1G
mkfs.ext2 -q -d "$tmpdir/dist" -L GL_TESTS "$output"

# GCP does not support plain raw disks as images, so we need to create a tar.gz file that contains a file called disk.raw
cp "${output}" "${output/dist.ext2.raw/disk.raw}"
tar -C "$(dirname "$output")" -czf "$output".tar.gz disk.raw
rm "${output/dist.ext2.raw/disk.raw}"

# Azure needs a vhd file with specific parameters and with a specific aligned size
qemu-img convert -f raw -O vpc -o subformat=fixed,force_size "$output" "${output/.raw/.vhd}"

# Ali needs a qcow2 file
qemu-img convert -f raw -O qcow "$output" "${output/.raw/.qcow2}"
