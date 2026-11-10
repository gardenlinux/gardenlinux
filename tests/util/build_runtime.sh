#!/usr/bin/env bash

set -eufo pipefail

tmpdir=

cleanup() {
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

verify_checksum() {
	# $1: expected sha256, $2: file
	printf '%s  %s\n' "$1" "$2" | sha256sum -c --status -
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

# TEMPORARY FIX for https://github.com/actions/runner-images/issues/14473
function podman() { command podman --runtime "$(command -v crun)" "$@"; }

if [ "$0" != /init ]; then
	cat >"$tmpdir/Containerfile" <<-'EOF'
		FROM debian:stable
		RUN apt-get update \
		&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl
	EOF

	podman build -q --iidfile "$tmpdir/image_id" "$tmpdir" >/dev/null
	image_id="$(<"$tmpdir/image_id")"

	cleanup
	exec podman run --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w "/mnt" "$image_id" /init "$@"
fi

requirements="$1"
python_env="$2"
output="$3"
target_arch="$4"  # required: amd64 or arm64 (Garden Linux arch naming)

# shellcheck source=tests/util/python.env.sh
source "$python_env"

case "$target_arch" in
amd64)
	kernel_arch="x86_64"
	expected_checksum="$PYTHON_ARCHIVE_CHECKSUM_AMD64"
	;;
arm64)
	kernel_arch="aarch64"
	expected_checksum="$PYTHON_ARCHIVE_CHECKSUM_ARM64"
	;;
*)
	echo "Unsupported target_arch: '$target_arch' (expected 'amd64' or 'arm64')" >&2
	exit 1
	;;
esac

python_lib_dir="lib/python${PYTHON_VERSION_SHORT}/site-packages"

mkdir "$tmpdir/runtime"

cache_dir=".cache"
mkdir -p "$cache_dir"

mkdir "$tmpdir/runtime/$target_arch"
archive_url="${PYTHON_SOURCE}/${RELEASE_DATE}/cpython-${PYTHON_VERSION}%2B${RELEASE_DATE}-${kernel_arch}-unknown-linux-gnu-install_only.tar.gz"
archive_name="cpython-${PYTHON_VERSION}+${RELEASE_DATE}-${kernel_arch}-unknown-linux-gnu-install_only.tar.gz"
archive_file_cached="$cache_dir/$archive_name"

if ! [ -f "$archive_file_cached" ] || ! verify_checksum "$expected_checksum" "$archive_file_cached" 2>/dev/null; then
	tmp_download="$archive_file_cached.partial"
	curl -sSLf "$archive_url" -o "$tmp_download"
	if ! verify_checksum "$expected_checksum" "$tmp_download"; then
		echo "Checksum mismatch for $target_arch after download" >&2
		rm -f "$tmp_download"
		exit 1
	fi
	mv -f "$tmp_download" "$archive_file_cached"
fi

archive_file="$archive_file_cached"

tar -x -z -f "$archive_file" -C "$tmpdir/runtime/$target_arch" --strip-components 1

# Install Python dependencies into the target runtime's site-packages.
# Pure-Python wheels are architecture-neutral, so we can run pip from the
# target runtime's own python when the host arch matches, or fall back to
# the host's native python (installing with --target) when cross-building.
host_kernel_arch="$(uname -m)"
case "$host_kernel_arch" in
x86_64) host_gl_arch="amd64" ;;
aarch64) host_gl_arch="arm64" ;;
*)
	echo "Unsupported host arch: $host_kernel_arch" >&2
	exit 1
	;;
esac

target_site_packages="$tmpdir/runtime/$target_arch/$python_lib_dir"

if [ "$host_gl_arch" = "$target_arch" ]; then
	# Native build: use the target runtime's own python directly.
	PATH="$tmpdir/runtime/$target_arch/bin:$PATH" pip install -q --root-user-action ignore --disable-pip-version-check --only-binary=:none: -r "$requirements"
else
	# Cross-arch build: use the host's python to install pure-Python wheels
	# into the target runtime's site-packages directory.
	case "$host_gl_arch" in
	amd64) host_checksum="$PYTHON_ARCHIVE_CHECKSUM_AMD64" ;;
	arm64) host_checksum="$PYTHON_ARCHIVE_CHECKSUM_ARM64" ;;
	esac
	host_archive_name="cpython-${PYTHON_VERSION}+${RELEASE_DATE}-${host_kernel_arch}-unknown-linux-gnu-install_only.tar.gz"
	host_archive_url="${PYTHON_SOURCE}/${RELEASE_DATE}/cpython-${PYTHON_VERSION}%2B${RELEASE_DATE}-${host_kernel_arch}-unknown-linux-gnu-install_only.tar.gz"
	host_archive_cached="$cache_dir/$host_archive_name"
	if ! [ -f "$host_archive_cached" ] || ! verify_checksum "$host_checksum" "$host_archive_cached" 2>/dev/null; then
		host_tmp_download="$host_archive_cached.partial"
		curl -sSLf "$host_archive_url" -o "$host_tmp_download"
		if ! verify_checksum "$host_checksum" "$host_tmp_download"; then
			echo "Checksum mismatch for host arch $host_gl_arch after download" >&2
			rm -f "$host_tmp_download"
			exit 1
		fi
		mv -f "$host_tmp_download" "$host_archive_cached"
	fi
	mkdir -p "$tmpdir/host-runtime"
	tar -x -z -f "$host_archive_cached" -C "$tmpdir/host-runtime" --strip-components 1
	PATH="$tmpdir/host-runtime/bin:$PATH" pip install -q --root-user-action ignore --disable-pip-version-check --only-binary=:none: --target "$target_site_packages" --upgrade -r "$requirements"
fi

tar -c -C "$tmpdir/runtime" . | gzip >"$output"
