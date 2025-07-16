#!/usr/bin/env bash

set -eufo pipefail

REGISTRY="ghcr.io/gardenlinux"
ARTIFACT_NAME="tests-ng"
OCI_APPLICATION_NAMESPACE="application/vnd.gardenlinux.tests-ng"
OCI_MEDIA_TYPE_PREFIX="${OCI_APPLICATION_NAMESPACE}.dist.v1"

usage() {
    cat <<EOF
Usage: $0 [-t TAG]... -f FILE [-f FILE]...

Upload tests-ng distribution as OCI artifact to GitHub Container Registry.

Options:
    -t TAG        Additional tag for the artifact (can be used multiple times)
    -f FILE       File to upload (can be used multiple times, required)
    -c CHECKSUM   Checksum of the test-ng distribution (optional)
EOF
}

additional_tags=()
files=()

while getopts "t:f:c:h" opt; do
    case $opt in
    t)
        additional_tags+=("$OPTARG")
        ;;
    f)
        files+=("$OPTARG")
        ;;
    c)
        checksum="$OPTARG"
        ;;
    h)
        usage
        exit 0
        ;;
    *)
        usage
        exit 1
        ;;
    esac
done

shift $((OPTIND - 1))

if [ $# -ne 0 ]; then
    echo "Error: Unexpected positional arguments"
    usage
    exit 1
fi

if [ ${#files[@]} -eq 0 ]; then
    echo "Error: No files specified (use -f)"
    usage
    exit 1
fi

if ! command -v oras >/dev/null 2>&1; then
    echo "Error: oras command not found"
    exit 1
fi

commit=$(test -z "$(git status --porcelain)" &&
    echo "$(git rev-parse --short HEAD)" ||
    echo "$(git rev-parse --short HEAD)-dirty")

tags=("latest" "${additional_tags[@]}")

if [ -n "${GITHUB_TOKEN:-}" ]; then
    echo "$GITHUB_TOKEN" | oras login ghcr.io -u dummy --password-stdin
fi

# Create temporary directory for flat file structure
TEMP_DIR=$(mktemp -d)
trap "rm -rf '$TEMP_DIR'" EXIT

file_args=()
for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: File does not exist: $file"
        exit 1
    fi

    base_file=$(basename "$file")
    # Copy file to temp directory with flat name
    cp "$file" "$TEMP_DIR/$base_file"

    if [[ "$base_file" == *.tar.gz ]]; then
        file_args+=("$base_file:${OCI_MEDIA_TYPE_PREFIX}+tar+gzip")
    elif [[ "$base_file" == *.tgz ]]; then
        file_args+=("$base_file:${OCI_MEDIA_TYPE_PREFIX}+tar+gzip")
    elif [[ "$base_file" == *.tar ]]; then
        file_args+=("$base_file:${OCI_MEDIA_TYPE_PREFIX}+tar")
    elif [[ "$base_file" == *.zip ]]; then
        file_args+=("$base_file:${OCI_MEDIA_TYPE_PREFIX}+zip")
    elif [[ "$base_file" == *.json ]]; then
        file_args+=("$base_file:${OCI_MEDIA_TYPE_PREFIX}+json")
    elif [[ "$base_file" == *.txt ]]; then
        file_args+=("$base_file:${OCI_MEDIA_TYPE_PREFIX}+text")
    else
        echo "Error: Unsupported file type: $file"
        exit 1
    fi
done

annotations=()
annotations+=("--annotation" "org.opencontainers.image.description=Garden Linux test framework")
annotations+=("--annotation" "gardenlinux.io/test-framework-name=pytest")
annotations+=("--annotation" "gardenlinux.io/test-framework-commit=${commit}")
annotations+=("--annotation" "gardenlinux.io/test-framework-supported-archs=x86_64,aarch64")
if [ -n "${checksum:-}" ]; then
    annotations+=("--annotation" "gardenlinux.io/test-framework-checksum=${checksum}")
fi

# Change to temp directory to upload flat file structure
cd "$TEMP_DIR"
oras push "$REGISTRY/$ARTIFACT_NAME:${tags[0]}" \
    "${annotations[@]}" \
    "${file_args[@]}"

for tag in "${tags[@]:1}"; do
    oras tag "$REGISTRY/$ARTIFACT_NAME:${tags[0]}" "$tag"
done
