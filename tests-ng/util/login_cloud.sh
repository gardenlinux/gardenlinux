#!/usr/bin/env bash

set -eufo pipefail

while [ $# -gt 0 ]; do
    case "$1" in
    *)
        break
        ;;
    esac
done

image="$1"
shift
image_basename="$(basename -- "$image")"
image_name=${image_basename/.*/}
workspace="$image_name"

util_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")")"
tf_dir="$util_dir/tf"
tofuenv_dir="$tf_dir/.tofuenv"
PATH="$tofuenv_dir/bin:$PATH"
ssh_private_key="$util_dir/../.ssh/id_ed25519_gl"

vm_ip="$(cd "$tf_dir" && tofu workspace select "$workspace" >/dev/null && tofu output --raw vm_ip)"
ssh_user="$(cd "$tf_dir" && tofu workspace select "$workspace" >/dev/null && tofu output --raw ssh_user)"
ssh_opts=(-o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i "$ssh_private_key")

exec ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "$@"
