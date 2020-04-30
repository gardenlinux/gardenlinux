#!/usr/bin/env bash

rootfsDir=$1
cap_files="cap_files"

echo "testing for needed capabilities"

source helpers
if ! check_rootdir "${rootfsDir}"; then
	exit 1
fi

capFiles=$(find ${rootfsDir} -type f -exec getcap {} \; 2> /dev/null | awk -v p=${rootfsDir%/} '{ gsub(p, "", $1); print;}' | sort) 
capFilesDefined=$(sort ${cap_files})

if diff <(echo "$capFiles") <(echo "$capFilesDefined") > /dev/null; then
	echo "OK - all capabilities as expected"
else
	echo "FAIL - capabilities don't match"
	echo "       expected: $(echo ${capFilesDefined})"
	echo "       got     : $(echo ${capFiles})"
	rc=1
fi

exit $rc
