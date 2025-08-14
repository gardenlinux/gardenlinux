#!/usr/bin/env bash

set -eufo pipefail

workspace=
user="admin"

while [ $# -gt 0 ]; do
    case "$1" in
    --workspace)
        workspace="$2"
        shift 2
        ;;
    --user)
        user="$2"
        shift 2
        ;;
    *)
        break
        ;;
    esac
done

if [ -z "${workspace:-}" ]; then
    [ $# -ge 1 ]
    image="$1"
    shift
    image_basename="$(basename -- "$image")"
    workspace="$image_basename"
fi

tf_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/tf")"

vm_ip="$(cd "$tf_dir" && tofu workspace select "$workspace" >/dev/null && tofu output --raw vm_ip)"
ssh_opts=(-q -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no)

exec ssh "${ssh_opts[@]}" "$user@$vm_ip" "$@"
