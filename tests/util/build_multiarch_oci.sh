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

# Use a run-unique manifest tag so we don't collide with pre-existing local
# manifests or with other concurrent builds in the same podman storage.
tag="localhost/gardenlinux-tests-multiarch-$$:latest"

cleanup() {
	podman manifest rm "$tag" 2>/dev/null || true
}
trap cleanup EXIT

# Build the manifest list directly from the per-arch OCI archives using the
# oci-archive: transport. Going through "podman load" and referring to the
# loaded images by their "localhost/..." tags makes podman try to resolve them
# against a (non-existent) registry in some environments, e.g. CI.
podman manifest create "$tag" >/dev/null
podman manifest add "$tag" "oci-archive:$input_amd64" >/dev/null
podman manifest add "$tag" "oci-archive:$input_arm64" >/dev/null

# --all includes the per-arch image blobs in the output archive so it is
# self-contained (loadable without a registry).
podman manifest push --compression-format zstd --compression-level 10 --all "$tag" "oci-archive:$output"
