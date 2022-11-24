#!/usr/bin/env bash
set -Eeuo pipefail

cat

cat << EOF
REPART=99    /bind_mounts    ext4    rw    weight=4
bind         /var
bind         /home
EOF
