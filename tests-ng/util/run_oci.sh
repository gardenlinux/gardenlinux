#!/usr/bin/env bash

set -eufo pipefail

test_args=()
bare=0

while [ $# -gt 0 ]; do
    case "$1" in
    --test-args)
        # Split the second argument on spaces to handle multiple test arguments
        IFS=' ' read -ra args <<<"$2"
        test_args+=("${args[@]}")
        shift 2
        ;;
    --bare)
        bare=1
        shift
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
log_dir="$root_dir/tests-ng/log"
log_file_log="oci.test-ng.log"
log_file_junit="oci.test-ng.xml"
test_dist_dir="$root_dir/tests-ng/.build"

mkdir -p "$log_dir"

if [ -z "$image" ]; then
    echo "Usage: $0 [--bare] <base-image|bare-image>" >&2
    echo "Examples:" >&2
    echo "  $0 .build/container-amd64-today-local.oci" >&2
    echo "  $0 --bare .build/bare_flavors/python-amd64.oci" >&2
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

if ((bare)); then
    echo "⚙️  building bare test container $image_name"
    cd "$root_dir/bare_flavors/$config/test"
    podman build -t test-run-oci --build-arg image="$image_sha" .

    echo "🚀  running bare test container $image_name"
    podman run --rm test-run-oci "${test_args[@]}" 2>&1 | tee "$log_dir/$log_file_log"
else
    echo "🚀  running test container $image_name"

    test_args+=("--junit-xml=$log_dir/$log_file_junit")
    test_args+=("--allow-system-modifications")
    test_args+=("--expected-users $USER")
    test_cmd="mkdir -p /run/gardenlinux-tests && tar -xz -C /run/gardenlinux-tests < /mnt/test_dist/dist.tar.gz && /run/gardenlinux-tests/run_tests ${test_args[*]}"
    podman run \
        --rm -it \
        -v "$test_dist_dir/dist.tar.gz:/mnt/test_dist/dist.tar.gz:ro" \
        -v "$log_dir:$log_dir:rw" \
        "$image_sha" /bin/sh -c "$test_cmd" 2>&1 | tee "$log_dir/$log_file_log"
fi
