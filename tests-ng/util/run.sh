#!/usr/bin/env bash

set -eufo pipefail

cloud=

cloud_image=0
chroot_args=()
cloud_args=()
qemu_args=()

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
	--cloud-plan)
		cloud_args+=("$1")
		shift
		;;
	--image-requirements-file)
		cloud_args+=("$1")
		cloud_args+=("$2")
		shift 2
		;;
	--ssh)
		qemu_args+=("$1")
		shift
		;;
	--only-cleanup)
		cloud_args+=("$1")
		shift
		;;
	--skip-cleanup)
		cloud_args+=("$1")
		qemu_args+=("$1")
		shift
		;;
	--skip-tests)
		cloud_args+=("$1")
		qemu_args+=("$1")
		shift
		;;
	--test-args)
		chroot_args+=("$1" "$2")
		cloud_args+=("$1" "$2")
		qemu_args+=("$1" "$2")
		shift 2
		;;
	*)
		break
		;;
	esac
done

if ((cloud_image)); then
	# When using --cloud-image, the artifact is the first positional argument (e.g., AMI ID)
	artifact="$1"

	# We also need to find the requirements file for configuration
	requirements_file=""
	for i in "${!cloud_args[@]}"; do
		if [[ "${cloud_args[$i]}" == "--image-requirements-file" && $((i + 1)) -lt ${#cloud_args[@]} ]]; then
			requirements_file="${cloud_args[$((i + 1))]}"
			break
		fi
	done

	if [[ -z "$requirements_file" ]]; then
		echo "Error: Could not find image requirements file in arguments" >&2
		exit 1
	fi

	# Make the requirements file path absolute since we'll change directory later
	requirements_file="$(realpath "$requirements_file")"

	# Update the cloud_args to use the absolute path
	for i in "${!cloud_args[@]}"; do
		if [[ "${cloud_args[$i]}" == "--image-requirements-file" ]]; then
			cloud_args[i + 1]="$requirements_file"
			break
		fi
	done
else
	artifact="$(realpath "$1")"
fi
cd "$(realpath -- "$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")/../")"

basename="$(basename "$artifact")"

extension="$(grep -E -o '(\.[a-z][a-zA-Z0-9_\-]*)*$' <<<"$basename")"
cname="${basename%"$extension"}"
type="${extension#.}"

[ -n "$cname" ]
if [ -z "$cloud" ] && ! ((cloud_image)); then
	[ -n "$type" ]
fi

./util/build.makefile

if [ -n "$cloud" ]; then
	if ((cloud_image)); then
		./util/run_cloud.sh --cloud "$cloud" --cloud-image "${cloud_args[@]}" .build "$artifact"
	else
		if [ "$type" != raw ]; then
			echo "cloud run only supported with raw file" >&2
			exit 1
		fi
		./util/run_cloud.sh --cloud "$cloud" "${cloud_args[@]}" .build "$artifact"
	fi
else
	case "$type" in
	tar)
		./util/run_chroot.sh "${chroot_args[@]}" .build "$artifact"
		;;
	raw)
		./util/run_qemu.sh "${qemu_args[@]}" .build "$artifact"
		;;
	*)
		echo "artifact type $type not supported" >&2
		exit 1
		;;
	esac
fi
