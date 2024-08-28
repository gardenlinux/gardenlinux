#!/usr/bin/env bash
set -euo pipefail

flavor="${1}"
flavor_safe=${flavor//-/_}
platform="${flavor%%-*}"

tofu output -json | \
    jq -r 'to_entries[] | .key + "=" + (.value.value | tostring)' | \
    while read -r line ; do echo export "${line}"; done | \
    tee "env.${flavor}.sh"

source "env.${flavor}.sh"
echo "#!/usr/bin/env bash" > "login.${flavor}.sh"
eval "echo ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -l \${${platform}_ssh_user} -i ${ssh_private_key} \${${flavor_safe}_public_ip}" >>"login.${flavor}.sh"
chmod +x "login.${flavor}.sh"
