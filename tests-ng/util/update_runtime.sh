#!/usr/bin/env bash

# Update Python version data in python.env.sh from upstream GitHub releases

set -eufo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_ENV_FILE="${SCRIPT_DIR}/python.env.sh"

TEMP_FILES=()

cleanup() {
    for temp_file in "${TEMP_FILES[@]}"; do
        [ -f "$temp_file" ] && rm -f "$temp_file"
    done
}

trap cleanup EXIT INT TERM

create_temp_file() {
    local temp_file
    temp_file=$(mktemp)
    TEMP_FILES+=("$temp_file")
    echo "$temp_file"
}

error() {
    echo "Error: $*" >&2
    exit 1
}

info() {
    echo "Info: $*" >&2
}

check_dependencies() {
    local missing=()

    if ! command -v jq &>/dev/null; then
        missing+=("jq")
    fi

    if ! command -v gh &>/dev/null; then
        missing+=("gh")
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        error "Missing required dependencies: ${missing[*]}"
    fi
}

read_python_version_short() {
    if [ ! -f "$PYTHON_ENV_FILE" ]; then
        error "File not found: $PYTHON_ENV_FILE"
    fi

    # shellcheck source=/dev/null
    source "$PYTHON_ENV_FILE"

    if [ -z "$PYTHON_VERSION_SHORT" ]; then
        error "Could not read PYTHON_VERSION_SHORT from $PYTHON_ENV_FILE"
    fi

    if [ -z "$PYTHON_REPO_OWNER" ]; then
        error "Could not read PYTHON_REPO_OWNER from $PYTHON_ENV_FILE"
    fi

    if [ -z "$PYTHON_REPO_NAME" ]; then
        error "Could not read PYTHON_REPO_NAME from $PYTHON_ENV_FILE"
    fi

    info "Current PYTHON_VERSION_SHORT: $PYTHON_VERSION_SHORT"
    info "Repository: $PYTHON_REPO_OWNER/$PYTHON_REPO_NAME"
}

find_matching_release() {
    local version_short="$1"
    local repo="${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}"
    local release_tags
    local release_json
    local tag

    local releases_json_file
    releases_json_file=$(create_temp_file)

    if ! gh release list --repo "$repo" --limit 30 --json tagName >"$releases_json_file" 2>/dev/null; then
        rm -f "$releases_json_file"
        error "Failed to get releases from GitHub"
    fi

    if [ ! -s "$releases_json_file" ]; then
        rm -f "$releases_json_file"
        error "Empty response from GitHub API"
    fi

    set +e
    jq -e . >/dev/null 2>/dev/null <"$releases_json_file"
    local validate_exit=$?
    set -e

    if [ $validate_exit -ne 0 ]; then
        rm -f "$releases_json_file"
        error "Invalid JSON received from GitHub API"
    fi

    set +e
    local release_tags
    release_tags=$(jq -r '.[].tagName' <"$releases_json_file" 2>/dev/null)
    local jq_exit=$?
    set -e

    if [ $jq_exit -ne 0 ]; then
        rm -f "$releases_json_file"
        error "Failed to parse release tags"
    fi
    rm -f "$releases_json_file"

    if [ -z "$release_tags" ]; then
        error "No releases found"
    fi

    while IFS= read -r tag; do
        [ -z "$tag" ] && continue

        info "Checking release $tag for Python $version_short..."

        local temp_json
        temp_json=$(create_temp_file)

        if ! gh release view --repo "$repo" "$tag" --json tagName,assets >"$temp_json" 2>/dev/null; then
            rm -f "$temp_json"
            continue
        fi

        if [ ! -s "$temp_json" ]; then
            rm -f "$temp_json"
            continue
        fi

        set +e
        jq -e . >/dev/null 2>/dev/null <"$temp_json"
        local validate_exit=$?
        set -e

        if [ $validate_exit -ne 0 ]; then
            rm -f "$temp_json"
            continue
        fi

        if jq -r --arg version "$version_short" '
            .assets[]?.name | select(test("cpython-" + $version + "\\.[0-9]+.*x86_64-unknown-linux-gnu.*install_only\\.tar\\.gz$"))
        ' <"$temp_json" | grep -q .; then
            info "Found matching release: $tag"
            cat "$temp_json"
            rm -f "$temp_json"
            return 0
        fi

        rm -f "$temp_json"
    done <<<"$release_tags"

    error "No release found containing assets for Python version $version_short"
}

extract_release_info() {
    local release_json="$1"
    local version_short="$2"
    local release_json_file
    release_json_file=$(create_temp_file)

    echo "$release_json" >"$release_json_file"

    local tag_name
    tag_name=$(jq -r '.tagName' <"$release_json_file")

    RELEASE_DATE=$(echo "$tag_name" | grep -oE '[0-9]{8}' || error "Could not extract release date from tag: $tag_name")

    local x86_64_asset
    x86_64_asset=$(jq -r --arg version "$version_short" '.assets[] | select(.name | test("cpython-" + $version + "\\.[0-9]+.*x86_64-unknown-linux-gnu.*install_only\\.tar\\.gz$")) | @json' <"$release_json_file" | head -n1)

    local aarch64_asset
    aarch64_asset=$(jq -r --arg version "$version_short" '.assets[] | select(.name | test("cpython-" + $version + "\\.[0-9]+.*aarch64-unknown-linux-gnu.*install_only\\.tar\\.gz$")) | @json' <"$release_json_file" | head -n1)

    if [ -z "$x86_64_asset" ] || [ "$x86_64_asset" = "null" ]; then
        error "Could not find x86_64 asset in release"
    fi

    if [ -z "$aarch64_asset" ] || [ "$aarch64_asset" = "null" ]; then
        error "Could not find aarch64 asset in release"
    fi

    local checksums_asset_url
    local checksums_content
    checksums_asset_url=$(jq -r '.assets[] | select(.name == "SHA256SUMS") | .url' <"$release_json_file" | head -n1)

    if [ -n "$checksums_asset_url" ] && [ "$checksums_asset_url" != "null" ]; then
        local repo="${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}"
        checksums_content=$(gh release download --repo "$repo" "$tag_name" --pattern "SHA256SUMS" --output - 2>/dev/null || true)

        if [ -n "$checksums_content" ]; then
            local x86_64_filename
            x86_64_filename=$(echo "$x86_64_asset" | jq -r '.name')
            PYTHON_ARCHIVE_CHECKSUM_AMD64=$(echo "$checksums_content" | grep "$x86_64_filename" | awk '{print $1}' | head -n1)

            local aarch64_filename
            aarch64_filename=$(echo "$aarch64_asset" | jq -r '.name')
            PYTHON_ARCHIVE_CHECKSUM_ARM64=$(echo "$checksums_content" | grep "$aarch64_filename" | awk '{print $1}' | head -n1)
        fi
    fi

    if [ -z "$PYTHON_ARCHIVE_CHECKSUM_AMD64" ] || [ -z "$PYTHON_ARCHIVE_CHECKSUM_ARM64" ]; then
        PYTHON_ARCHIVE_CHECKSUM_AMD64=$(echo "$x86_64_asset" | jq -r '.digest // empty' | sed 's/^sha256://')
        PYTHON_ARCHIVE_CHECKSUM_ARM64=$(echo "$aarch64_asset" | jq -r '.digest // empty' | sed 's/^sha256://')
    fi

    if [ -z "$PYTHON_ARCHIVE_CHECKSUM_AMD64" ] || [ -z "$PYTHON_ARCHIVE_CHECKSUM_ARM64" ]; then
        error "Could not extract checksums for required architectures"
    fi

    if ! echo "$PYTHON_ARCHIVE_CHECKSUM_AMD64" | grep -qE '^[0-9a-f]{64}$'; then
        error "Invalid AMD64 checksum format"
    fi

    if ! echo "$PYTHON_ARCHIVE_CHECKSUM_ARM64" | grep -qE '^[0-9a-f]{64}$'; then
        error "Invalid ARM64 checksum format"
    fi

    local asset_name
    asset_name=$(echo "$x86_64_asset" | jq -r '.name')

    PYTHON_VERSION=$(echo "$asset_name" | sed -n 's/^cpython-\([0-9]\+\.[0-9]\+\.[0-9]\+\)+.*/\1/p')

    if [ -z "$PYTHON_VERSION" ]; then
        error "Could not extract PYTHON_VERSION from asset name: $asset_name"
    fi

    rm -f "$release_json_file"
}

update_python_env_file() {
    local temp_file
    temp_file=$(create_temp_file)

    # Read old values for comparison
    local old_version old_date old_amd64 old_arm64
    old_version=$(grep -E '^export PYTHON_VERSION=' "$PYTHON_ENV_FILE" | sed 's/^export PYTHON_VERSION="\(.*\)"/\1/' || echo "")
    old_date=$(grep -E '^export RELEASE_DATE=' "$PYTHON_ENV_FILE" | sed 's/^export RELEASE_DATE="\(.*\)"/\1/' || echo "")
    old_amd64=$(grep -E '^export PYTHON_ARCHIVE_CHECKSUM_AMD64=' "$PYTHON_ENV_FILE" | sed 's/^export PYTHON_ARCHIVE_CHECKSUM_AMD64="\(.*\)"/\1/' || echo "")
    old_arm64=$(grep -E '^export PYTHON_ARCHIVE_CHECKSUM_ARM64=' "$PYTHON_ENV_FILE" | sed 's/^export PYTHON_ARCHIVE_CHECKSUM_ARM64="\(.*\)"/\1/' || echo "")

    while IFS= read -r line; do
        case "$line" in
        export\ PYTHON_VERSION=*)
            echo "export PYTHON_VERSION=\"$PYTHON_VERSION\""
            ;;
        export\ RELEASE_DATE=*)
            echo "export RELEASE_DATE=\"$RELEASE_DATE\""
            ;;
        export\ PYTHON_ARCHIVE_CHECKSUM_AMD64=*)
            echo "export PYTHON_ARCHIVE_CHECKSUM_AMD64=\"$PYTHON_ARCHIVE_CHECKSUM_AMD64\""
            ;;
        export\ PYTHON_ARCHIVE_CHECKSUM_ARM64=*)
            echo "export PYTHON_ARCHIVE_CHECKSUM_ARM64=\"$PYTHON_ARCHIVE_CHECKSUM_ARM64\""
            ;;
        *)
            echo "$line"
            ;;
        esac
    done <"$PYTHON_ENV_FILE" >"$temp_file"

    if cmp -s "$PYTHON_ENV_FILE" "$temp_file"; then
        info "No changes needed - file is already up to date"
        rm -f "$temp_file"
        return 1
    fi

    mv "$temp_file" "$PYTHON_ENV_FILE"
    info "Updated $PYTHON_ENV_FILE"

    # Print what changed
    local changed_fields=()
    if [ "$old_version" != "$PYTHON_VERSION" ]; then
        changed_fields+=("PYTHON_VERSION: $old_version -> $PYTHON_VERSION")
    fi
    if [ "$old_date" != "$RELEASE_DATE" ]; then
        changed_fields+=("RELEASE_DATE: $old_date -> $RELEASE_DATE")
    fi
    if [ "$old_amd64" != "$PYTHON_ARCHIVE_CHECKSUM_AMD64" ]; then
        changed_fields+=("PYTHON_ARCHIVE_CHECKSUM_AMD64: ${old_amd64:0:16}... -> ${PYTHON_ARCHIVE_CHECKSUM_AMD64:0:16}...")
    fi
    if [ "$old_arm64" != "$PYTHON_ARCHIVE_CHECKSUM_ARM64" ]; then
        changed_fields+=("PYTHON_ARCHIVE_CHECKSUM_ARM64: ${old_arm64:0:16}... -> ${PYTHON_ARCHIVE_CHECKSUM_ARM64:0:16}...")
    fi

    if [ ${#changed_fields[@]} -gt 0 ]; then
        info "Updated fields:"
        for field in "${changed_fields[@]}"; do
            info "  $field"
        done
    fi

    return 0
}

main() {
    info "Starting Python runtime update..."

    check_dependencies
    read_python_version_short

    info "Finding latest release matching Python $PYTHON_VERSION_SHORT..."
    local release_json
    release_json=$(find_matching_release "$PYTHON_VERSION_SHORT")

    extract_release_info "$release_json" "$PYTHON_VERSION_SHORT"

    if update_python_env_file; then
        info "Successfully updated Python version data"
        return 0
    else
        return 0
    fi
}

main "$@"
