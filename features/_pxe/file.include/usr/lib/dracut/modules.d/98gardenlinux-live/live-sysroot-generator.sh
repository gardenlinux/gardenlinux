#!/bin/bash

command -v getarg >/dev/null || . /lib/dracut-lib.sh

set -e

GENERATOR_DIR=$1

getarg gl.ovl= > /dev/null || exit 0
ovlconf=$(getarg gl.ovl=)
ovlconf=${ovlconf#gl.ovl=}

# if an overlay is predefined for sysroot, skip sysroot.mount generation
if echo "$ovlconf" | grep -q '^/:\|,/:'; then
	exit 0
fi

GENERATOR_DIR="$1"

cat >"${GENERATOR_DIR}/sysroot.mount" <<EOF
[Unit]
After=live-get-squashfs.service
Before=initrd-root-fs.target
DefaultDependencies=no

[Mount]
What=/run/root.squashfs
Where=/sysroot
Type=squashfs
Options=loop
EOF

mkdir -p "$GENERATOR_DIR"/initrd-root-fs.target.requires
ln -s ../sysroot.mount "$GENERATOR_DIR"/initrd-root-fs.target.requires/sysroot.mount
