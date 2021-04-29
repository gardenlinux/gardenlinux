#!/bin/bash

command -v getarg >/dev/null || . /lib/dracut-lib.sh

GENERATOR_DIR=$1

ovlconf=$(getarg gl.ovl=)
ovlconf=${ovlconf#gl.ovl=}

if [ -z "$ovlconf" ]; then
    exit 0
fi

echo $ovlconf | awk -F, 'BEGIN {OFS="\n"}; {$1=$1; gsub(/:/, " "); print}' > /tmp/overlay.conf

# add a test for /tmp/overlay.conf
if [ ! -f /tmp/overlay.conf ]; then
    echo "there is no /tmp/overlay.conf - exiting"
    exit 1
fi

mkdir -p /run/overlay

# check if overlay for root is wanted
if echo "$ovlconf" | grep -q '^/:\|,/:'; then
	# we have overlay for root defined, ignore everything else
	dev=$(grep '^/ ' /tmp/overlay.conf | awk '{print $2}')
	devescape=$(systemd-escape -p --suffix=service "$dev")
	mkdir -p "/run/sysroot.ovl"

	if [[ "$dev" != tmpfs ]]; then	
		echo "[Unit]
		Before=sysroot.mount
		After=ignition-disks.service
		DefaultDependencies=no
		Requires=systemd-fsck@${devescape}
		After=systemd-fsck@${devescape}

		[Mount]
		What=$dev
		Where=/run/sysroot.ovl" | awk '{$1=$1}1' > "${GENERATOR_DIR}/run-sysroot.ovl.mount"

		mkdir ${GENERATOR_DIR}/systemd-fsck@${devescape}.d

            	echo "[Unit]
            	After=ignition-disks.service" > ${GENERATOR_DIR}/systemd-fsck@${devescape}.d/after-ignition-disks.conf
	fi
	
	echo "[Unit]
	After=run-sysroot.ovl.mount
	After=ignition-disks.service
	Before=sysroot.mount
	DefaultDependencies=no

	[Service]
	Type=oneshot
	User=root
	Group=root
	ExecStart=/bin/mkdir -p /run/sysroot.ovl/upper /run/sysroot.ovl/work" | awk '{$1=$1}1' > "${GENERATOR_DIR}/create-mountpoints.service"
	
	echo "[Unit]
	Before=initrd-root-fs.target
	After=run-rootfs.mount
	After=ignition-disks.service
	After=create-mountpoints.service
	DefaultDependencies=no
	Description=sysroot.mount
	[Mount]
	What=ovl_sysroot
	Where=/sysroot
	Type=overlay
	Options=lowerdir=/run/rootfs,upperdir=/run/sysroot.ovl/upper,workdir=/run/sysroot.ovl/work" | awk '{$1=$1}1' > "${GENERATOR_DIR}/sysroot.mount"

	mkdir -p "$GENERATOR_DIR"/initrd-root-fs.target.requires
	ln -s ../sysroot.mount "$GENERATOR_DIR"/initrd-root-fs.target.requires/sysroot.mount
	if [[ "$dev" != tmpfs ]]; then	
		ln -s ../run-sysroot.ovl.mount "$GENERATOR_DIR"/initrd-root-fs.target.requires/run-sysroot.ovl.mount
	fi
	ln -s ../create-mountpoints.service "$GENERATOR_DIR"/initrd-root-fs.target.requires/create-mountpoints.service

	exit 0
fi

while read -r line; do
	what=$(echo "$line" | awk '{ print $1}')
	where=$(echo "$line" | awk '{ print $2}')
	dev=$(echo "$line" | awk '{ print $3}')
	unit=$(systemd-escape -p --suffix=mount "/sysroot$what")
	if [ "$where" == "tmpfs" ]; then
		upper="/run/overlay$what-upper"
		work="/run/overlay$what-work"
		mkdir -p "$upper"
		mkdir -p "$work"
	else
		# FIXME for disks handled by ignition - this will fail on squashfs
		# FIXME persistent overlays should probably be handled fully by ignition
		upper="/sysroot/$where/up"
		work="/sysroot/$where/work"
	fi


	{
	echo "[Unit]"
	echo "Before=initrd-root-fs.target"
	echo "After=sysroot.mount"
	echo "DefaultDependencies=no"
	echo "Description=$unit"
	
	echo "[Mount]"
	echo "What=ovl_$what"
	echo "Where=/sysroot$what"
	echo "Type=overlay"
	echo "Options=lowerdir=/sysroot$what,upperdir=$upper,workdir=$work"
	} > "$GENERATOR_DIR/$unit"

	mkdir -p "$GENERATOR_DIR"/initrd-root-fs.target.requires
	ln -s ../$unit $GENERATOR_DIR/initrd-root-fs.target.requires/$unit
done < /tmp/overlay.conf

exit 0
