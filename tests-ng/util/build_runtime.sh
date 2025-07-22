#!/usr/bin/env bash

set -eufo pipefail

set -x

PYTHON_SOURCE="https://github.com/astral-sh/python-build-standalone/releases/download"
PYTHON_VERSION_SHORT="3.13"
PYTHON_VERSION="$PYTHON_VERSION_SHORT.5"
RELEASE_DATE="20250712"
PYTHON_ARCHIVE_CHECKSUM_AMD64="9af1a2a3a3c06ee7fd264e677a551c399fa534f92ecdafbbb3e8b4af34adcb84"
PYTHON_ARCHIVE_CHECKSUM_ARM64="d3b6805d8a12610d45917aa5cac69f53f8dd1ee3faef86fc8d2d1488825edd9a"
CACHE_DIR=".cache"

tmpdir=

cleanup() {
	[ -n "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

validate_checksum() {
	local arch_pkg="$1"
	local file_path="$2"
	local checksum_var="PYTHON_ARCHIVE_CHECKSUM_$(echo ${arch_pkg} | tr '[:lower:]' '[:upper:]')"
	local expected_checksum=${!checksum_var}
	local actual_checksum=$(sha256sum "$file_path" | cut -d' ' -f1)

	if [ "$actual_checksum" != "$expected_checksum" ]; then
		echo "Checksum mismatch for $arch_pkg"
		echo "Expected: $expected_checksum"
		echo "Actual: $actual_checksum"
		exit 1
	fi
}

get_arch_pkg() {
	local arch="$1"
	case "$arch" in
	aarch64) echo "arm64" ;;
	x86_64) echo "amd64" ;;
	*)
		echo "Unsupported architecture: $arch" >&2
		exit 1
		;;
	esac
}

get_python_archive_name() {
	local arch="$1"
	echo "cpython-${PYTHON_VERSION}%2B${RELEASE_DATE}-${arch}-unknown-linux-gnu-install_only.tar.gz"
}

download_and_extract_python() {
	local arch="$1"
	local target_dir="$2"
	local arch_pkg=$(get_arch_pkg "$arch")
	local python_tgz=$(get_python_archive_name "$arch")

	mkdir -p "$target_dir"
	test -f "$CACHE_DIR/${python_tgz}" || curl -sSLf "${PYTHON_SOURCE}/${RELEASE_DATE}/${python_tgz}" -o "$CACHE_DIR/${python_tgz}"
	validate_checksum "$arch_pkg" "$CACHE_DIR/${python_tgz}"
	gzip -dc "$CACHE_DIR/${python_tgz}" | tar -x -C "$target_dir" --strip-components 1
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

if [ "$0" != /init ]; then
	cat >"$tmpdir/Containerfile" <<-'EOF'
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
arch_target_pkg=$(get_arch_pkg "$arch_target")
arch_host_pkg=$(get_arch_pkg "$arch_host")

requirements="$2"
output="$3"

requirements_hash=$(sha256sum "$requirements" | cut -d' ' -f1 | cut -c1-8)
cache_filename="runtime-${arch_target}-${PYTHON_VERSION}-${RELEASE_DATE}-${requirements_hash}.tar.gz"
cache_path="${CACHE_DIR}/${cache_filename}"

if [ -f "$cache_path" ]; then
	echo "Using cached runtime: $cache_filename"
	cp "$cache_path" "$output"
	exit 0
fi
mkdir -p "$CACHE_DIR"

download_and_extract_python "$arch_target" "$tmpdir/runtime"

if [ "$arch_host" != "$arch_target" ]; then
	download_and_extract_python "$arch_host" "$tmpdir/host_runtime"
else
	mkdir "$tmpdir/host_runtime"
	(cd "$tmpdir/runtime" && cp -r . "$tmpdir/host_runtime/")
fi

PATH="$tmpdir/host_runtime/bin:$PATH"
PYTHONPATH="$tmpdir/runtime/lib/python${PYTHON_VERSION_SHORT}/site-packages"
mkdir -p "$tmpdir/runtime/lib/python${PYTHON_VERSION_SHORT}/site-packages"
# NOTE: as for now, we should not depend on any binary packages
pip install --only-binary=:none: --target "$tmpdir/runtime/lib/python${PYTHON_VERSION_SHORT}/site-packages" -r "$requirements"
find "$tmpdir/runtime/lib/python${PYTHON_VERSION_SHORT}/site-packages" -type d -name __pycache__ -exec rm -rf {} +

tar -c -C "$tmpdir/runtime" . | gzip >"$output"
cp "$output" "$cache_path"
find "$CACHE_DIR" -name "runtime-${arch_target}-*" ! -name "$cache_filename" -delete 2>/dev/null || true
