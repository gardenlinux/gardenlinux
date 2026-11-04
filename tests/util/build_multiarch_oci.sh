#!/usr/bin/env bash

set -eufo pipefail

dist_dir="$1"
output="$2"

input_amd64="$dist_dir/dist-amd64.oci"
input_arm64="$dist_dir/dist-arm64.oci"

for f in "$input_amd64" "$input_arm64"; do
	if [ ! -f "$f" ]; then
		echo "missing input OCI archive: $f" >&2
		exit 1
	fi
done

# Use a run-unique tag so we don't collide with pre-existing local images
# or with other concurrent builds in the same podman storage.
tag="localhost/gardenlinux-tests-multiarch-$$:latest"

cleanup() {
	podman manifest rm "$tag" 2>/dev/null || true
	podman rmi -f "$amd64_id" "$arm64_id" 2>/dev/null || true
}
trap cleanup EXIT

amd64_id="$(podman load -q -i "$input_amd64" | awk '{ print $NF }')"
arm64_id="$(podman load -q -i "$input_arm64" | awk '{ print $NF }')"

if [ -z "$amd64_id" ] || [ -z "$arm64_id" ]; then
	echo "failed to load one or both OCI archives" >&2
	exit 1
fi

podman manifest create "$tag" "$amd64_id" "$arm64_id" >/dev/null

# --all includes the per-arch image blobs in the output archive so it is
# self-contained (loadable without a registry).
podman manifest push --all "$tag" "oci-archive:$output"
