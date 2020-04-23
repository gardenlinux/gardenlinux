#!/usr/bin/env bash

rootfsDir=$1
targetBaseDir=$2

rc=0
echo "checking for an empty /proc"
nr=$(shopt -s nullglob dotglob; f=(${rootfsDir}/proc/*); echo ${#f[@]})

if [[ "$nr" -ne 0 ]]; then
	echo "/proc is not empty!"
	echo "expected: 0"
	echo "got:      ${nr}"
	rc=1
fi

exit $rc
