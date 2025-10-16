#!/bin/bash

# shellcheck disable=SC2046,SC2006,SC2086
WORKDIR="$(realpath $(dirname `basename $0`))"
IMAGE_NAME="busybox:1.37.0-uclibc"
TARBALL_AMD64="${WORKDIR}/../plugins/busybox_amd64.tar"
TARBALL_ARM64="${WORKDIR}/../plugins/busybox_arm64.tar"
FAILED=""

cleanup() {
  podman --noout rmi -i ${IMAGE_NAME}
}

assert() {
  local x y failure_message; x="$1"; y="$2"; failure_message="$3"

  if [ "$x" != "$y" ]; then
    FAILED="${FAILED}\n- ${failure_message} ($x vs $y)"
  fi
}

pull_original_image() {
  local arch; arch="$1"

  podman --noout pull -q --arch "${arch}" ${IMAGE_NAME}
}

cleanup; pull_original_image amd64

assert "$(podman inspect "${IMAGE_NAME}" | jq '.[].RootFS.Layers | length')" 1 \
  "number of layers in amd64 registry image is not equal 1"

assert "$(tar -xOf "${TARBALL_AMD64}" manifest.json | jq -r '.[].Layers | length')" 1 \
  "number of layers in amd64 tarball image is not equal 1"

assert "$(podman inspect "${IMAGE_NAME}" | jq -r '.[].RootFS.Layers[0] | ltrimstr("sha256:")')" \
  "$(tar -xOf "${TARBALL_AMD64}" manifest.json | jq -r '.[].Layers[0] | rtrimstr(".tar")')" \
  "checksums of data layers for amd64 images do not match"


cleanup; pull_original_image arm64

assert "$(podman inspect "${IMAGE_NAME}" | jq '.[].RootFS.Layers | length')" 1 \
  "number of layers in arm64 registry image is not equal 1"

assert "$(tar -xOf "${TARBALL_ARM64}" manifest.json | jq -r '.[].Layers | length')" 1 \
  "number of layers in arm64 tarball image is not equal 1"

assert "$(podman inspect "${IMAGE_NAME}" | jq -r '.[].RootFS.Layers[0] | ltrimstr("sha256:")')" \
  "$(tar -xOf "${TARBALL_ARM64}" manifest.json | jq -r '.[].Layers[0] | rtrimstr(".tar")')" \
  "checksums of data layers for arm64 images do not match"

if [ -n "$FAILED" ]; then 
  echo "Validation failed:"
  echo -e "$FAILED"
  exit 1
fi
