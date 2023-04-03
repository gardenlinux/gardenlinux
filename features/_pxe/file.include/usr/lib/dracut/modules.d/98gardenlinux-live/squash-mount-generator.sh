#!/bin/bash

command -v getarg >/dev/null || . /lib/dracut-lib.sh

set -e

GENERATOR_DIR="$1"

mkdir -p /run/rootfs

if [ ! -e /run/root.squashfs ]; then
	if [ -e /root.squashfs ]; then
		mv /root.squashfs /run/root.squashfs
	else
		getarg gl.url= > /dev/null || exit 0
		cat >"${GENERATOR_DIR}/live-get-squashfs.service" <<-EOF
		[Unit]
		Description=Download squashfs image

		After=network-online.target systemd-resolved.service
		Wants=network-online.target systemd-resolved.service

		OnFailure=emergency.target
		OnFailureJobMode=isolate
		DefaultDependencies=no

		[Service]
		Type=oneshot
		TimeoutStartSec=600
		RemainAfterExit=yes
		ExecStart=/sbin/live-get-squashfs
		EOF
	fi
fi

cat >"${GENERATOR_DIR}/run-rootfs.mount" <<EOF
[Unit]
After=live-get-squashfs.service
Wants=live-get-squashfs.service
After=dracut-pre-mount.service
Before=initrd-root-fs.target
DefaultDependencies=no

[Mount]
What=/run/root.squashfs
Where=/run/rootfs
Type=squashfs
Options=loop
EOF
