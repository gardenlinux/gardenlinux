#!/usr/bin/env bash

set -eufo pipefail
set -x

cloud=
cloud_image=0
arch=
cloud_args=()

while [ $# -gt 0 ]; do
	case "$1" in
	--cloud)
		cloud="$2"
		shift 2
		;;
	--cloud-image)
		cloud_image=1
		shift
		;;
	--arch)
		arch="$2"
		shift 2
		;;
	--skip-cleanup)
		cloud_args+=("$1")
		shift
		;;
	--scp)
		cloud_args+=("$1")
		shift
		;;
	*)
		break
		;;
	esac
done

if ((cloud_image)); then
	artifact="$1"
else
	artifact="$(realpath "$1")"
fi
cd "$(realpath -- "$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")/../")"

basename="$(basename "$artifact")"

extension="$(grep -E -o '(\.[a-z][a-zA-Z0-9_\-]*)*$' <<<"$basename")"
cname="${basename%"$extension"}"
type="${extension#.}"
[ -n "$arch" ] || arch="$(awk -F '-' '{ print $(NF-2) }' <<<"$cname")"

if [ "$arch" = "amd64" ]; then
	arch="x86_64"
fi

[ -n "$cname" ] && [ -n "$type" ] && [ -n "$arch" ]

./util/build.makefile

if [ -n "$cloud" ]; then
	if ((cloud_image)); then
		./util/run_cloud.sh --cloud "$cloud" --cloud-image --arch "$arch" "${cloud_args[@]}" .build "$artifact"
	else
		if [ "$type" != raw ]; then
			echo "cloud run only supported with raw file" >&2
			exit 1
		fi
		./util/run_cloud.sh --cloud "$cloud" --arch "$arch" "${cloud_args[@]}" .build "$artifact"
	fi
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
