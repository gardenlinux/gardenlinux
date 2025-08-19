#!/usr/bin/env bash

set -eufo pipefail

ssh_user=gardenlinux

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
ssh_opts=(-p 2222 -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no)

exec ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "$@"
