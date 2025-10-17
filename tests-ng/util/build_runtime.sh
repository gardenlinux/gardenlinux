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

if [ "$0" != /init ]; then
	cat >"$tmpdir/Containerfile" <<-'EOF'
		FROM debian:stable
		RUN apt-get update \
		&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl retry
	EOF

	podman build -q --iidfile "$tmpdir/image_id" "$tmpdir" >/dev/null
	image_id="$(<"$tmpdir/image_id")"

	cleanup
	exec podman run --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w "/mnt" "$image_id" /init "$@"
fi

requirements="$1"
python_env="$2"
output="$3"

# shellcheck source=tests-ng/util/python.env.sh
source "$python_env"

python_lib_dir="lib/python${PYTHON_VERSION_SHORT}/site-packages"

mkdir "$tmpdir/runtime"
mkdir "$tmpdir/site-packages"

cache_dir=".cache"
mkdir -p "$cache_dir"

for arch in x86_64 aarch64; do
	mkdir "$tmpdir/runtime/$arch"
	archive_url="${PYTHON_SOURCE}/${RELEASE_DATE}/cpython-${PYTHON_VERSION}%2B${RELEASE_DATE}-${arch}-unknown-linux-gnu-install_only.tar.gz"
	archive_name="cpython-${PYTHON_VERSION}+${RELEASE_DATE}-${arch}-unknown-linux-gnu-install_only.tar.gz"
	archive_file_cached="$cache_dir/$archive_name"

	case "$arch" in
	x86_64)
		expected_checksum="$PYTHON_ARCHIVE_CHECKSUM_AMD64"
		;;
	aarch64)
		expected_checksum="$PYTHON_ARCHIVE_CHECKSUM_ARM64"
		;;
	*)
		echo "Unsupported arch: $arch" >&2
		exit 1
		;;
	esac

	if ! [ -f "$archive_file_cached" ] || ! verify_checksum "$expected_checksum" "$archive_file_cached" 2>/dev/null; then
		tmp_download="$archive_file_cached.partial"
		retry -d "1,2,5,10,30" curl -sSLf "$archive_url" -o "$tmp_download"
		if ! verify_checksum "$expected_checksum" "$tmp_download"; then
			echo "Checksum mismatch for $arch after download" >&2
			rm -f "$tmp_download"
			exit 1
		fi
		mv -f "$tmp_download" "$archive_file_cached"
	fi

	archive_file="$archive_file_cached"

	tar -x -z -f "$archive_file" -C "$tmpdir/runtime/$arch" --strip-components 1

	if [ ! -e "$tmpdir/runtime/site-packages" ]; then
		mv "$tmpdir/runtime/$arch/$python_lib_dir" "$tmpdir/runtime/site-packages"
	else
		rm -rf "$tmpdir/runtime/$arch/$python_lib_dir"
	fi
	ln -s ../../../site-packages "$tmpdir/runtime/$arch/$python_lib_dir"
done

arch="$(uname -m)"
PATH="$tmpdir/runtime/$arch/bin:$PATH"
pip install -q --root-user-action ignore --disable-pip-version-check --only-binary=:none: -r "$requirements"
tar -c -C "$tmpdir/runtime" . | gzip >"$output"
