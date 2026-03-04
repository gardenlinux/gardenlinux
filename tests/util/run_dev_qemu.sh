#!/usr/bin/env bash

set -eufo pipefail

util_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")")"
ssh_private_key="$util_dir/../.ssh/id_ed25519_gl"

vm_ip="127.0.0.1"
ssh_user=gardenlinux
ssh_opts=(-p 2222 -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i "$ssh_private_key")

source "$util_dir/run_dev_common.sh"
