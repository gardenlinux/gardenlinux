#!/bin/bash
#set -Eeuo pipefail

cname="$@"

arch="$(gl-features-parse --cname "${cname}" arch)"
cname_base="$(gl-features-parse --cname "${cname}" cname_base)"
bare_flavor="${cname_base//bare-/}"

image="$(podman load < .build/bare_flavors/${bare_flavor}-${arch}.oci | awk '{ print $NF }')"
cd bare_flavors/${bare_flavor}/test
podman build -t test --build-arg image="$image" .
podman run --rm test
