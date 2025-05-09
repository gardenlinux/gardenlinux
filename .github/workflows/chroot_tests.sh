#!/bin/bash
#set -Eeuo pipefail

cname="${@: -1}"

podman build --squash --tag test --build-arg base=debian:stable tests
./test --container-image test "${cname}"
