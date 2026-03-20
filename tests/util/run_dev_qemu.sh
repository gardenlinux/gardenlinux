#!/usr/bin/env bash

set -eufo pipefail

util_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")")"
ssh_private_key="$util_dir/../.ssh/id_ed25519_gl"

export vm_ip="127.0.0.1"
export ssh_user=gardenlinux
export ssh_opts=(-q -p 2222 -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i "$ssh_private_key")

# shellcheck source=/dev/null
source "$util_dir/run_dev_common.sh"
