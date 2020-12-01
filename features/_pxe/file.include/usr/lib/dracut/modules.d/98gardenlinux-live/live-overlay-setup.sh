#!/bin/bash

command -v getarg >/dev/null || . /lib/dracut-lib.sh

GENERATOR_DIR=$1

ovlconf=$(getarg gl.ovl=)
ovlconf=${ovlconf#gl.ovl=}

if [ -z "$ovlconf" ]; then
	echo "/var tmpfs" >> /tmp/overlay.conf
	echo "/etc tmpfs" >> /tmp/overlay.conf
	info "Generated overlay.conf - /etc and /var will be overlayed using tmpfs"
else
	echo $ovl | awk -F, 'BEGIN {OFS="\n"}; {$1=$1; gsub(/:/, " "); print}' > /tmp/overlay.conf
fi


# add a test for /tmp/overlay.conf
if ! test -f /tmp/overlay.conf; then
	echo "there is no /tmp/overlay.conf - exiting"
	exit 1
fi

mkdir /run/overlay

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
