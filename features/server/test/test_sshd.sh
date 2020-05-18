#!/usr/bin/env bash

set -e 
echo "executing ssh config tests"
rootfsDir=$1

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
	run_in_chroot ${rootfsDir} chroot_sshd.sh ssh_expected ssh_not_expected  
fi
