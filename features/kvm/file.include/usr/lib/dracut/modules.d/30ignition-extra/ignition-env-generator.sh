#!/bin/bash

set -e

GENERATOR_DIR=$1

for i in /etc/ignition-*.env; do
	if [ ! -f "$i" ]; then
		exit 0
	fi	       
	f=$(basename $i)
	p=$(echo "${GENERATOR_DIR}/${f%%.env}.service.d")
	mkdir -p "$p"
	{
	echo "[Service]"
	while read -r line; do
		echo Environment=\"$line\"
	done < "$i"	
	}> "$p/env.conf"
done

exit 0
