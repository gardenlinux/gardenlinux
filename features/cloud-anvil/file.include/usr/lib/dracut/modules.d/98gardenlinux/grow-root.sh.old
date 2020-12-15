#!/bin/sh

# From : https://github.com/larsks/cloud-initramfs-tools/blob/master/growroot/dracut/modules.d/50growroot/growroot.sh

# Environment variables that this script relies upon:
# - NEWROOT

. /lib/dracut-lib.sh

# This is a table of commands necessary to fsck particular filesystem
# types prior to resizing them.  Defining an fsck command means that
# it must succeed for the resize to be attempted.
FSCK_ext2="e2fsck -fp"
FSCK_ext3="e2fsck -fp"
FSCK_ext4="e2fsck -fp"

# This is a table of commands necessary to resize particular
# filesystem types.
RESIZE_ext2=resize2fs
RESIZE_ext3=resize2fs
RESIZE_ext4=resize2fs
RESIZE_xfs=xfs_growfs

_info() {
	echo "growroot: $*"
}

_warning() {
	echo "growroot Warning: $*" >&2
}

# This will drop us into an emergency shell
_fatal() {
	echo "growroot Fatal: $*" >&2
	exit 1
}

# This runs right before exec of /sbin/init, the real root is already mounted
# at NEWROOT
_growroot()
{
	local out rootdev rootmnt rootfs opts unused rootdisk partnum

	# If a file indicates we should do nothing, then just return
	for file in /var/lib/cloud/instance/root-grown /etc/growroot-disabled \
		/etc/growroot-grown ; do
		if [ -f "${NEWROOT}${file}" ] ; then
			_info "${file} exists, nothing to do"
			return
		fi
	done

	# Get the root device, root filesystem and mount options
	if ! out=$(awk '$2 == mt { print }' "mt=${NEWROOT}" < /proc/mounts) ; then
	_warning "${out}"
	return
	fi

	# Need to do it this way, can't use '<<< "${out}"' since RHEL6 doesn't
	# seem to understand it
	read rootdev rootmnt rootfs opts unused <<EOF
${out}
EOF
	if [ -z "{rootdev}" -o -z "${rootmnt}" -o -z "${rootfs}" -o \
		-z "${opts}" ] ; then
	_warning "${out}"
	return
	fi

	# If the basename of the root device (ie 'xvda1', 'sda1', 'vda') exists
	# in /sys/block/ then it is a block device, not a partition
	if [ -e "/sys/block/${rootdev##*/}" ] ; then
		_info "${rootdev} is not a partition"
		return
	fi

	# Check if the root device is a partition (name ends with a digit)
	if [ "${rootdev%[0-9]}" = "${rootdev}" ] ; then
		_warning "${rootdev} is not a partition"
		return
	fi

	# Remove all numbers from the end of rootdev to get the rootdisk and
	# partition number
	rootdisk=${rootdev}
	while [ "${rootdisk%[0-9]}" != "${rootdisk}" ] ; do
		rootdisk=${rootdisk%[0-9]}
	done
	partnum=${rootdev#${rootdisk}}

	# Do a growpart dry run and exit if it fails or doesn't have anything to do
	if ! out=$(growpart --dry-run "${rootdisk}" "${partnum}") ; then
		_info "${out}"
		return
	fi

	# There's something to do so unmount and re-partition
	if ! umount "${NEWROOT}" ; then
		_warning "Failed to umount ${NEWROOT}"
		return
	fi

	# Wait for any of the initial udev events to finish otherwise growpart
	# might fail
	udevsettle

	# Resize the root partition
	if out=$(growpart "${rootdisk}" "${partnum}" 2>&1) ; then
		_info "${out}"
	else
		_warning "${out}"
		_warning "growpart failed"
	fi

	# Wait for the partition re-read events to complete so that the root
	# partition is available for remounting
	udevsettle

	eval fsck_cmd="\"\${FSCK_${rootfs}}\""
	eval resize_cmd="\"\${RESIZE_${rootfs}}\""

	if [ "$resize_cmd" ]; then
			# fsck the filesystem if required.  because e2fsck will sometimes return
			# an error code even when there are no problems, we just ignore failures
			# here and assume that the resize command will bail if something is 
			# actually wrong.
			if [ "$fsck_cmd" ]; then
					$fsck_cmd "${rootdev}"
			fi

			# A failed resize generates a warning but we allow the boot to
			# continue.
			$resize_cmd "${rootdev}" || \
					_warning "failed to resize ${rootdev}"
	fi

	# Remount the root filesystem
	mount -t "${rootfs}" -o "${opts}" "${rootdev}" "${NEWROOT}" || \
		_fatal "Failed to re-mount ${rootdev}, this is bad"

	# Write to /etc/growroot-grown, most likely this wont work (read-only)
	{
		date --utc > "${NEWROOT}/etc/growroot-grown"
	} >/dev/null 2>&1
}

_growroot

# vi: ts=4 noexpandtab
