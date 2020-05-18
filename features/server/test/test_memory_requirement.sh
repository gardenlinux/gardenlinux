#!/usr/bin/env bash

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

run_in_chroot ${rootfsDir} chroot_memory_requirement.sh  
