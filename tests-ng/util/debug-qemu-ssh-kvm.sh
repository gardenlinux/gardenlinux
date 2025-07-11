#!/usr/bin/env bash

git_root=$(git rev-parse --show-toplevel)

set -eufo pipefail

# Check if kvm image exists and build it if missing
test -f "${git_root}/.build/kvm-gardener_prod-amd64-today-local.raw" || ( cd ${git_root} && make kvm-gardener_prod-amd64-build )

# Check if qemu-kvm-gardener_prod-amd64 is running and start it if missing
podman ps | grep qemu-kvm-gardener_prod-amd64 || make --directory=tests/platformSetup kvm-gardener_prod-amd64-qemu-apply

# ... This will take some time up until ssh is up

# Prepare directory for tests-ng
CMD="rm -rf /var/tmp/tests-ng && mkdir -p /var/tmp/tests-ng" make --directory=tests/platformSetup kvm-gardener_prod-amd64-qemu-login

# Copy over tests-ng
SCP_PATH_LOCAL="/gardenlinux/tests-ng/.build/dist.tar.gz" SCP_PATH_REMOTE="/var/tmp/tests-ng" make --directory=tests/platformSetup kvm-gardener_prod-amd64-qemu-scp-local-remote

# Run tests-ng
CMD="gzip -d < /var/tmp/tests-ng/dist.tar.gz | tar -x && ./run_tests" make --directory=tests/platformSetup kvm-gardener_prod-amd64-qemu-login

# Remove tests-ng
CMD="rm -rf /var/tmp/tests-ng" make --directory=tests/platformSetup kvm-gardener_prod-amd64-qemu-login
