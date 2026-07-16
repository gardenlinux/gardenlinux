#!/usr/bin/env bash

set -eufo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 [--watch] [--test-args \"...\"] IMAGE" >&2
    exit 1
fi

# Treat the last positional argument as the image, everything before it
# is forwarded to run_dev_common.sh (e.g. --watch, --test-args, --user).
args=("$@")
image="${args[${#args[@]} - 1]}"
unset 'args[${#args[@]}-1]'
set -- "${args[@]}"

image_basename="$(basename -- "$image")"
image_name="${image_basename%.*}"

util_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")")"
ssh_private_key="$util_dir/../.ssh/id_ed25519_gl"

tf_dir="$util_dir/tf"
tofuenv_dir="$tf_dir/.tofuenv"
PATH="$tofuenv_dir/bin:$PATH"
uuid_file="$util_dir/.uuid"
uuid=$(<"$uuid_file")
seed=${uuid%%-*}

if [ -n "${GITHUB_RUN_ID:-}" ] && [ -n "${GITHUB_RUN_NUMBER:-}" ]; then
    workspace="test-${GITHUB_RUN_ID}-${GITHUB_RUN_NUMBER}-${image_name}-${seed}"
else
    workspace="test-${image_name}-${seed}"
fi

echo "⚙️  getting terraform outputs"
vm_ip="$(cd "$tf_dir" && tofu workspace select "$workspace" >/dev/null && tofu output --raw vm_ip)"
ssh_user="$(cd "$tf_dir" && tofu workspace select "$workspace" >/dev/null && tofu output --raw ssh_user)"
echo "📋  VM IP: $vm_ip, SSH User: $ssh_user"
export ssh_opts=(-q -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i "$ssh_private_key")

# shellcheck source=/dev/null
source "$util_dir/run_dev_common.sh"
