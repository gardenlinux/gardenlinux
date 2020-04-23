#!/usr/bin/env bash

rootfsDir=$1
targetBaseDir=$2

rc=0
echo "checking for empty/shadowed passwords"
if ! out=$(awk -F: '$2~/\*/ { next; } $2~/!/ { next; } {print $0; exit 1}' ${rootfsDir}/etc/shadow); then
	echo "following problems detected for no passwords should be set:"
	echo "$out"
	rc=1
fi
out=""
if ! out=$(awk -F: '$2~/\*/ { next; } $2~/x/ { next; } {print $0; exit 1}' ${rootfsDir}/etc/passwd); then
	echo "following problems detected for shadowed passwords:"
	echo "$out"
	rc=1
fi

exit $rc
