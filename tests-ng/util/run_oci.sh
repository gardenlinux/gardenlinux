#!/usr/bin/env bash

set -eufo pipefail

skip_tests=0
test_args=()

while [ $# -gt 0 ]; do
    case "$1" in
    --skip-tests)
        skip_tests=1
        shift
        ;;
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
log_dir="$root_dir/tests-ng/log"
log_file_log="oci.test-ng.log"
log_file_junit="oci.test-ng.xml"

mkdir -p "$log_dir"
test_args+=("--junit-xml=/run/gardenlinux-tests/log/$log_file_junit")

# Extract test artifact name from image filename
test_artifact="$(basename "$image" | sed 's/.oci$//')"
test_type="oci"
test_namespace="test-ng"

# Add pytest-metadata arguments
test_args+=("--metadata" "Artifact" "$test_artifact")
test_args+=("--metadata" "Type" "$test_type")
test_args+=("--metadata" "Namespace" "$test_namespace")

echo "📊  metadata: Artifact=$test_artifact, Type=$test_type, Namespace=$test_namespace"

if [ -z "$image" ]; then
    echo "Usage: $0 <oci-image>" >&2
    echo "Example: $0 .build/container-amd64-today-local.oci" >&2
    exit 1
fi

cleanup() {
    echo "⚙️  cleaning up containers and images $image_name"
    podman rmi -f "$image_sha" 2>/dev/null || true
}

trap cleanup EXIT

echo "⚙️  loading OCI image $image_name"
image_sha="$(podman load -q --input "$image" 2>/dev/null | awk '{ print $NF }')"

test_args+=(
    "--allow-system-modifications"
)

echo "🚀  running test container $image_name"

run_args=(
    "--pull" "never"
    "--rm"
    "-v" "$root_dir/tests-ng/.build/dist.tar.gz:/run/gardenlinux-tests/dist.tar.gz:ro"
    "-v" "$log_dir:/run/gardenlinux-tests/log:rw"
)

if ((skip_tests)); then
    run_args+=(
        "-it"
        "$image_sha"
        "bash"
    )
else
    run_args+=(
        "$image_sha"
        "bash"
        "-c"
        "cd /run/gardenlinux-tests && \
            tar xzf dist.tar.gz && \
            ./run_tests ${test_args[*]@Q} 2>&1 \
        "
    )
fi
podman run "${run_args[@]}" 2>&1 | tee "$log_dir/$log_file_log"
