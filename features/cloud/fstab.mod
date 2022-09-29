#!/usr/bin/env bash

set -Eeuo pipefail

while read -r line; do
	read -r source target fs options args <<< "$line"
	if [ "$target" = "/boot/efi" ]; then
		args="$args,size=128MiB"
		echo "$source $target $fs $options $args"
	else
		echo "$line"
	fi
done
