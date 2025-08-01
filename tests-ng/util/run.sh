#!/usr/bin/env bash

set -eufo pipefail

cloud=
cloud_args=()

while [ $# -gt 0 ]; do
	case "$1" in
		--cloud)
			cloud="$2"
			shift 2
			;;
		--skip-cleanup)
			cloud_args+=("$1")
			shift
			;;
		*)
			break
			;;
	esac
done

artifact="$(realpath "$1")"
cd "$(realpath -- "$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")/../")"

basename="$(basename "$artifact")"

cname="${basename%%.*}"
type="${basename#*.}"
arch="$(awk -F '-' '{ print $(NF-2) }' <<< "$cname")"

[ -n "$cname" ] && [ -n "$type" ] && [ -n "$arch" ]

./util/build.makefile

if [ -n "$cloud" ]; then
	if [ $type != raw ]; then
		echo "cloud run only supported with raw file" >&2
		exit 1
	fi

	./util/run_cloud.sh --cloud "$cloud" --arch "$arch" "${cloud_args[@]}" .build "$artifact"
else
	case "$type" in
		tar)
			./util/run_chroot.sh .build "$artifact"
			;;
		raw)
			./util/run_qemu.sh --arch "$arch" .build "$artifact"
			;;
		*)
			echo "artifact type $type not supported" >&2
			exit 1
			;;
	esac
fi
