#!/usr/bin/env bash

rootfsDir=$1

echo "executing tiger tests"
thisDir=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))
if [ -z ${thisDir} ]; then
	echo "FATAL - can't determine working directory"
	exit 1
fi

source ${thisDir}/helpers

if ! check_rootdir "${rootfsDir}"; then
	exit 1
fi

run_in_chroot ${rootfsDir} tiger.sh tigerrc  
