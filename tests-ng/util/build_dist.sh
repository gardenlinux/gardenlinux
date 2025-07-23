#!/usr/bin/env bash

set -eufo pipefail

set -x

# if [ "$0" != /init ]; then
# 	exec podman run --privileged -v /dev:/dev --device /dev/loop-control --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w /mnt debian:stable /bin/bash -c 'apt-get update && apt-get install -y qemu-utils && /init "$@"' -- "$@"
# fi

tmpdir=

cleanup() {
	[ -n "$tmpdir" ] && rm -rf "$tmpdir"
	tmpdir=
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

if [ "$0" != /init ]; then
	cat >"$tmpdir/Containerfile" <<-'EOF'
		FROM debian:stable
		RUN apt-get update \
		&& apt-get install -y --no-install-recommends ca-certificates curl libc6 make qemu-utils
	EOF

	podman build --iidfile "$tmpdir/image_id" "$tmpdir"
	image_id="$(<"$tmpdir/image_id")"

	cleanup
	exec podman run --privileged -v /dev:/dev --device /dev/loop-control --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w /mnt "$image_id" /init "$@"
fi

output="$1"
shift

# Parse optional formats parameter
formats_arg=""
if [[ "$1" == "--formats" ]]; then
	formats_arg="$2"
	shift 2
fi

# If no formats specified, build all formats
if [[ -z "$formats_arg" ]]; then
	formats=("raw" "vhd" "qcow2")
else
	IFS=',' read -ra formats <<<"$formats_arg"
fi

runtimes=("$@")

mkdir -p "$tmpdir/dist/runtime"

num_runtimes=${#runtimes[@]}

for runtime in "${runtimes[@]}"; do
	IFS=: read runtime_arch runtime_tar <<<"$runtime"
	mkdir "$tmpdir/dist/runtime/$runtime_arch"
	gzip -d <"$runtime_tar" | tar -x -C "$tmpdir/dist/runtime/$runtime_arch"
	# NOTE: as for now, we should not depend on any binary packages
	# therefore, we only need to keep the site-packages directory in the root of the runtime
	# and symlink it to the other architectures
	PYTHON_LIB_DIR="$(find $tmpdir/dist/runtime/$runtime_arch/lib -type d -name python*)"

	if [ "$num_runtimes" -gt 1 ]; then
		if [ "$runtime_arch" = "x86_64" ]; then
			mv "$PYTHON_LIB_DIR/site-packages" "$tmpdir/dist/runtime/site-packages"
		else
			rm -rf "$PYTHON_LIB_DIR/site-packages"
		fi
		(cd "$PYTHON_LIB_DIR" && ln -s ../../../site-packages)
	fi
done

set +f

mkdir -p "$tmpdir/dist/tests"
cp -r -t "$tmpdir/dist/tests" conftest.py plugins test_*.py

cat >"$tmpdir/dist/run_tests" <<'EOF'
#!/bin/sh

set -e

arch="$(uname -m)"
script_path="$(realpath -- "$0")"
script_dir="$(dirname -- "$script_path")"

export PATH="$script_dir/runtime/$arch/bin:$PATH"
PYTHON_LIB_DIR="$(find $script_dir/runtime/$(uname -m)/lib -type d -name python*)"
export PYTHONPATH="$PYTHON_LIB_DIR/site-packages"
cd "$script_dir/tests"
COLUMNS=120 python -m pytest -rA --tb=short --color=yes "$@"
EOF
chmod +x "$tmpdir/dist/run_tests"

tar -c -C "$tmpdir/dist" . | gzip >"$output"

# Create raw ext4 formated disk image containing the distribution
# These disks will be attached to the instances in the platform-tests
output_dir="$(dirname "$output")"
output_basename="$(basename "$output")"
disk_basename="${output_basename%.tar.gz}.disk.raw.tar.gz"
disk_output="$output_dir/$disk_basename"
checksummed_disk_basename="${output_basename%.tar.gz}.disk.raw"
checksummed_vhd_basename="${output_basename%.tar.gz}.disk.vhd"
checksummed_qcow2_basename="${output_basename%.tar.gz}.disk.qcow2"
disk_raw="$tmpdir/$checksummed_disk_basename"
disk_vhd="$tmpdir/$checksummed_vhd_basename"
disk_qcow2="$tmpdir/$checksummed_qcow2_basename"
mount_point="$tmpdir/mount"

qemu-img create -f raw "$disk_raw" 1G
# Use mkfs.ext4 with -d option to populate filesystem directly (avoids loop mounting)
mkfs.ext4 -F -d "$tmpdir/dist" "$disk_raw"

# Create the requested disk formats
for format in "${formats[@]}"; do
	case "$format" in
	"raw")
		cp "$disk_raw" "$output_dir/$checksummed_disk_basename"
		# GCP expects the disk to be named disk.raw
		tar -c -C "$tmpdir" --transform "s|$checksummed_disk_basename|disk.raw|" "$checksummed_disk_basename" | gzip >"$disk_output"
		;;
	"vhd")
		# Create VHD version for Azure (fixed format required)
		qemu-img convert -f raw -O vpc -o subformat=fixed,force_size "$disk_raw" "$disk_vhd"
		cp "$disk_vhd" "$output_dir/$checksummed_vhd_basename"
		vhd_tar_basename="${output_basename%.tar.gz}.disk.vhd.tar.gz"
		vhd_tar_output="$output_dir/$vhd_tar_basename"
		# Rename to disk.vhd to be consistent with the other formats
		tar -c -C "$tmpdir" --transform "s|$checksummed_vhd_basename|disk.vhd|" "$checksummed_vhd_basename" | gzip >"$vhd_tar_output"
		;;
	"qcow2")
		# Create QCOW2 version for OpenStack
		qemu-img convert -f raw -O qcow2 "$disk_raw" "$disk_qcow2"
		cp "$disk_qcow2" "$output_dir/$checksummed_qcow2_basename"
		qcow2_tar_basename="${output_basename%.tar.gz}.disk.qcow2.tar.gz"
		qcow2_tar_output="$output_dir/$qcow2_tar_basename"
		# Rename to disk.qcow2 to be consistent with the other formats
		tar -c -C "$tmpdir" --transform "s|$checksummed_qcow2_basename|disk.qcow2|" "$checksummed_qcow2_basename" | gzip >"$qcow2_tar_output"
		;;
	*)
		echo "Unknown format: $format" >&2
		exit 1
		;;
	esac
done
