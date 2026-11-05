#!/usr/bin/env bash

set -eufo pipefail

dist_dir="$1"
output="$2"
target_arch="$3"  # required: amd64 or arm64 (Garden Linux arch naming)

case "$target_arch" in
amd64 | arm64) ;;
*)
	echo "Unsupported target_arch: '$target_arch' (expected 'amd64' or 'arm64')" >&2
	exit 1
	;;
esac

container_dir="$(dirname -- "${BASH_SOURCE[0]}")/container"
image_tag="localhost/gardenlinux-tests:${target_arch}"

podman build \
	--arch "$target_arch" \
	--build-context "dist_ctx=$dist_dir" \
	--build-arg "DIST_FILE=dist-${target_arch}.tar.gz" \
	-t "$image_tag" \
	"$container_dir"

podman save --format oci-archive "$image_tag" >"$output"
