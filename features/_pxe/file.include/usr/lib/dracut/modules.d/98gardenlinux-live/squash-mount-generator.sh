#!/bin/bash

command -v getarg >/dev/null || . /lib/dracut-lib.sh

set -e

GENERATOR_DIR="$1"

mkdir -p /run/rootfs

cat >"${GENERATOR_DIR}/run-rootfs.mount" <<EOF
[Unit]
After=live-get-squashfs.service
Before=initrd-root-fs.target
DefaultDependencies=no

[Mount]
What=/run/root.squashfs
Where=/run/rootfs
Type=squashfs
Options=loop
EOF

mkdir -p "$GENERATOR_DIR"/initrd-root-fs.target.requires
ln -s ../run-rootfs.mount "$GENERATOR_DIR"/initrd-root-fs.target.requires/run-rootfs.mount
