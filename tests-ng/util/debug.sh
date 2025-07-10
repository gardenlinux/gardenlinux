#!/usr/bin/env bash

set -eufo pipefail

podman run --rm -v "$PWD/.build/dist.tar.gz:/mnt/dist.tar.gz:ro" --read-only --tmpfs /opt/tests -w /opt/tests ghcr.io/gardenlinux/gardenlinux /bin/bash -c 'gzip -d < /mnt/dist.tar.gz | tar -x && ./run_tests'
