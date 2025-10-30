#!/usr/bin/env bash

set -eufo pipefail

ssh_user=gardenlinux
util_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")")"
ssh_private_key="$util_dir/../.ssh/id_ed25519_gl"

while [ $# -gt 0 ]; do
    case "$1" in
    --user)
        ssh_user="$2"
        shift 2
        ;;
    *)
        break
        ;;
    esac
done

vm_ip="127.0.0.1"
ssh_opts=(-p 2222 -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i "$ssh_private_key")

exec ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "$@"
