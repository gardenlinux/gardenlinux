#!/bin/bash

command -v getarg >/dev/null || . /lib/dracut-lib.sh
set -e

# TODO: change the parameter name to illustrate better what it's used for
# should be gl.squashfs=url=http://...
# or gl.squashfs=dev=/dev/vdx

url=$(getarg gl.url=)
if [ -z "${url#gl.url=}" ] && [ ! -f /root.squashfs ]; then
	exit 0
fi

GENERATOR_DIR="$1"

# generator already ran, exit
if [ -e "${GENERATOR_DIR}/run-rootfs.mount" ]; then
	exit 0
fi

# squashfs embedded into the initrd
if [ -f /root.squashfs ]; then
	cat >"${GENERATOR_DIR}/run-rootfs.mount" <<-EOF
	[Unit]
	After=dracut-pre-mount.service
	Before=initrd-root-fs.target
	DefaultDependencies=no

	[Mount]
	What=/run/root.squashfs
	Where=/run/rootfs
	Type=squashfs
	Options=loop
	EOF
	cat >"${GENERATOR_DIR}/move-squashfs.service" <<-EOF
	[Unit]
	Description=Movesquashfs image

	OnFailure=emergency.target
	OnFailureJobMode=isolate
	DefaultDependencies=no

	[Service]
	Type=oneshot
	TimeoutStartSec=600
	RemainAfterExit=yes
	ExecStart=/bin/bash -c "mv /root.squashfs /run/root.squashfs"
	EOF
        mkdir -p "$GENERATOR_DIR"/basic.target.wants
        ln -s ../symlink-squashfs.service "$GENERATOR_DIR"/basic.target.wants/symlink-squashfs.service
	exit 0
fi

# we have squashfs attached as dev
if [[ "$url" == "/dev/"* ]]; then
	devname=$(dev_unit_name "$url")

	mkdir -p "$GENERATOR_DIR"/initrd-root-fs.target
	ln -s ../"${devname}".device "$GENERATOR_DIR"/initrd-root-fs.target/"${devname}".device

	mkdir -p "$GENERATOR_DIR"/"${devname}".device.d
	{
	echo "[Unit]"
	echo "JobTimeoutSec=30"
	echo "JobRunningTimeoutSec=30"
	} > "$GENERATOR_DIR"/"${devname}".device.d/timeout.conf

	cat >"${GENERATOR_DIR}/run-rootfs.mount" <<-EOF
	[Unit]
	After=$devname.device
	Wants=$devname.device

	After=dracut-pre-mount.service
	Before=initrd-root-fs.target
	DefaultDependencies=no

	[Mount]
	What=/run/root.squashfs
	Where=/run/rootfs
	Type=squashfs
	Options=loop
	EOF
	cat >"${GENERATOR_DIR}/symlink-squashfs.service" <<-EOF
	[Unit]
	Description=Symlink squashfs image

	OnFailure=emergency.target
	OnFailureJobMode=isolate
	DefaultDependencies=no

	[Service]
	Type=oneshot
	TimeoutStartSec=600
	RemainAfterExit=yes
	ExecStart=/bin/bash -c "ln -s $url /run/root.squashfs"
	EOF
        mkdir -p "$GENERATOR_DIR"/basic.target.wants
        ln -s ../symlink-squashfs.service "$GENERATOR_DIR"/basic.target.wants/symlink-squashfs.service
# we have a url
elif [[ "$url" == "http"* ]]; then
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
	cat >"${GENERATOR_DIR}/run-rootfs.mount" <<-EOF
	[Unit]
	After=live-get-squashfs.service
	Wants=live-get-squashfs.service
	#After=dracut-pre-mount.service
	#Before=initrd-root-fs.target
	DefaultDependencies=no
	[Mount]
	What=/run/root.squashfs
	Where=/run/rootfs
	Type=squashfs
	Options=loop
	EOF
        mkdir -p "$GENERATOR_DIR"/initrd-root-fs.target.requires
        ln -s ../live-get-squashfs.service "$GENERATOR_DIR"/initrd-root-fs.target.requires/live-get-squashfs.service
fi
