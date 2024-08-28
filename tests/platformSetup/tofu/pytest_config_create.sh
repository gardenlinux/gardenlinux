#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel)

flavor="${1}"
flavor_safe=${flavor//-/_}
platform="${flavor%%-*}"

source "env.${flavor}.sh"

public_ip=$(eval echo \${${flavor_safe}_public_ip})
ssh_user=$(eval echo \${${platform}_ssh_user})

sed "s#MY_IP#$public_ip#" "${ROOT_DIR}/tests/config/manual_${flavor}.yaml.template" >"${ROOT_DIR}/tests/config/manual_${flavor}.yaml"
sed -i "s#SSH_USER#$ssh_user#" "${ROOT_DIR}/tests/config/manual_${flavor}.yaml"
sed -i "s#SSH_PRIVATE_KEY#$ssh_private_key#" "${ROOT_DIR}/tests/config/manual_${flavor}.yaml"
