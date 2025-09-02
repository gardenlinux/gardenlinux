#!/usr/bin/env bash

set -eufo pipefail

test_args=()

while [ $# -gt 0 ]; do
    case "$1" in
    --test-args)
        # Split the second argument on spaces to handle multiple test arguments
        IFS=' ' read -ra args <<<"$2"
        test_args+=("${args[@]}")
        shift 2
        ;;
    *)
        break
        ;;
    esac
done

image="$2"
image_basename="$(basename -- "$image")"
image_name=${image_basename/.*/}
root_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/../..")"

if [ -z "$image" ]; then
    echo "Usage: $0 <bare-image>" >&2
    echo "Example: $0 .build/bare_flavors/python-amd64.oci" >&2
    exit 1
fi

config=$(echo "$image_name" | sed 's/-amd64//' | sed 's/-arm64//')

if [ ! -f "$image" ]; then
    echo "Error: OCI file not found: $image" >&2
    exit 1
fi

echo "⚙️  loading OCI image $image_name"
image_sha="$(podman load -qi "$image" 2>/dev/null | awk '{ print $NF }')"

if [ -z "$image_sha" ]; then
    echo "Error: Failed to extract image sha from podman load output." >&2
    exit 1
fi

cleanup() {
    echo "⚙️  cleaning up containers and images $image_name"
    podman rm -f test-run-oci 2>/dev/null || true
    podman rmi -f test-run-oci 2>/dev/null || true
    if [ -n "$image_sha" ]; then
        podman rmi -f "$image_sha" 2>/dev/null || true
    fi
}

trap cleanup EXIT

echo "⚙️  building test container $image_name"
cd "$root_dir/bare_flavors/$config/test"
podman build -t test-run-oci --build-arg image="$image_sha" .

echo "🚀  running test container $image_name"
podman run --rm test-run-oci "${test_args[@]}"
