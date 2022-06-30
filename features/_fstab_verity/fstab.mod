#!/usr/bin/env bash
set -Eeuo pipefail

# delete any predefinition of a overlay and root partition
sed '/^[^[:space:]]\+[[:space:]]\+\/overlay[[:space:]]\+/d;/^[^[:space:]]\+[[:space:]]\+\/[[:space:]]\+/d'

# make usr a readonly setup
printf "LABEL=ROOT         /            ext4      ro            verity\n"
printf "LABEL=OVERLAY      /overlay     ext4      rw,discard,x-initrd.mount    size=512MiB\n"
