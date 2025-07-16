#!/usr/bin/env bash
set -euo pipefail

REGISTRY=ghcr.io
REPOSITORY=gardenlinux/tests-ng
TAG=${1:-latest}

# default /tmp is mounted noexec
export TMPDIR=/var/tmp

# Function to make HTTP request using openssl for HTTPS
http_request() {
  local host="$1" path="$2" auth="$3" accept="$4" follow="${5:-true}"

  # Build and send request
  local req="GET $path HTTP/1.1\r\nHost: $host\r\nConnection: close\r\n"
  [ -n "$auth" ] && req+="Authorization: $auth\r\n"
  [ -n "$accept" ] && req+="Accept: $accept\r\n"
  req+="\r\n"

  local temp=$(mktemp)
  printf "%b" "$req" | openssl s_client -connect "$host:443" -quiet -servername "$host" -ign_eof 2>/dev/null >"$temp" || {
    rm -f "$temp"
    return 1
  }

  # Handle redirects
  local status=$(head -1 "$temp")
  if [[ "$status" =~ 30[1-8] && "$follow" == "true" ]]; then
    local location=$(grep -i "^Location:" "$temp" | cut -d' ' -f2- | tr -d '\r\n')
    if [[ "$location" =~ ^https://([^/]+)(/.*)$ ]]; then
      rm -f "$temp"
      http_request "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" "" "$accept" "false"
      return $?
    fi
  fi

  # Extract body (skip headers)
  local line_num=$(grep -a -n "^[[:space:]]*$" "$temp" | head -1 | cut -d: -f1)
  [ -n "$line_num" ] && tail -n +$((line_num + 1)) "$temp" || cat "$temp"
  rm -f "$temp"
}

TOKEN=$(http_request "${REGISTRY}" "/token?scope=repository:${REPOSITORY}:pull" "" "" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

[ -z "${TOKEN}" ] && {
  echo "Error: Could not get authentication token" >&2
  exit 1
}

MANIFEST=$(http_request "${REGISTRY}" "/v2/${REPOSITORY}/manifests/${TAG}" "Bearer ${TOKEN}" "application/vnd.oci.image.manifest.v1+json")

if command -v jq >/dev/null 2>&1; then
  DIGEST=$(echo "${MANIFEST}" | jq -r '.layers[] | select(.annotations."org.opencontainers.image.title" == "tests-ng-dist.tar.gz") | .digest')
else
  LAYER_BLOCK=$(echo "${MANIFEST}" | grep -o '{[^}]*"mediaType":"application/vnd\.gardenlinux\.tests-ng\.dist\.v1+tar+gzip"[^}]*}')
  DIGEST=$(echo "${LAYER_BLOCK}" | grep -o '"digest":"sha256:[^"]*"' | cut -d'"' -f4)
fi

[ -z "$DIGEST" ] && {
  echo "Error: Could not find digest for tests-ng-dist.tar.gz" >&2
  exit 1
}

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR" "$0"' EXIT

http_request "${REGISTRY}" "/v2/${REPOSITORY}/blobs/${DIGEST}" "Bearer ${TOKEN}" "" >"${TEMP_DIR}/blob.tar.gz"
tar -xzf "${TEMP_DIR}/blob.tar.gz" -C "${TEMP_DIR}"

[ -x "${TEMP_DIR}/run_tests" ] && {
  cd "${TEMP_DIR}"
  ./run_tests "$@"
}
