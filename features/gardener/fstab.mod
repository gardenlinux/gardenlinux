#!/usr/bin/env bash
set -Eeuo pipefail

# delete any predefinition of a usr partition
sed '/^[^[:space:]]\+[[:space:]]\+\/usr[[:space:]]\+/d'

# make usr a readonly setup
printf "LABEL=USR          /usr         ext4      ro\n"
