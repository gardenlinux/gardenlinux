#!/usr/bin/env bash

set -Eeuo pipefail

while read -r line; do
	read -r source target fs options args <<< "$line"
	if [ "$target" = "/efi" ]; then
		options="$options,noauto"
		args="$args,secureboot,size=128MiB"
		echo "$source $target $fs $options $args"
	else
		echo "$line"
	fi
done
