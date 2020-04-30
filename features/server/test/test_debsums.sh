#!/usr/bin/env bash

rootfsDir=$1

echo "testing the integrity of the files from installed packages"

relPath=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))
if [ -z ${relPath} ]; then
	echo "FATAL - can't determine working directory"
	exit 1
fi

source ${relPath}/helpers

if ! check_rootdir "${rootfsDir}"; then
	exit 1
fi

if [[ "$UID" -ne 0 ]]; then
	echo "FATAL - must be run as root"
	exit 1
else
	run_in_chroot ${rootfsDir} chroot_debsums.sh debsums_exclude  
fi
