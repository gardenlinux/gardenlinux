#!/usr/bin/env bash

set -eufo pipefail

artifact="$(realpath "$1")"
cd "$(realpath -- "$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")/../")"

basename="$(basename "$artifact")"

cname="${basename%%.*}"
type="${basename#*.}"
arch="$(awk -F '-' '{ print $(NF-2) }' <<< "$cname")"

[ -n "$cname" ] && [ -n "$type" ] && [ -n "$arch" ]

./util/build.makefile

case "$type" in
	tar)
		./util/run_chroot.sh .build "$artifact"
		;;
	raw)
		./util/run_qemu.sh .build "$arch" "$artifact"
		;;
	*)
		echo "artifact type $type not supported" >&2
		exit 1
		;;
esac
