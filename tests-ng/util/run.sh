#!/usr/bin/env bash

set -eufo pipefail

help() {
	cat <<EOF
Garden Linux Tests Next Generation (tests-ng)

Usage: ${0} [OPTIONS] ARTIFACT

DESCRIPTION
  This script automatically detects the image type and runs appropriate tests for Garden Linux images.
  It supports testing in various environments including chroot, QEMU virtual machines, and cloud providers.

COMMON OPTIONS
  --help                           Show this help message and exit

  --skip-cleanup                  Skip cleanup of cloud resources after testing
                                   QEMU VM: After running/skipping tests, stop/cleanup with ctrl+c
                                   Cloud: To cleanup resources after passing this flag, re-run without it

  --skip-tests                    Skip running the actual test suite

  --test-args <args>              Pass any commandline argument to pytest
                                   Put multiple arguments inside quotes

CLOUD SPECIFIC OPTIONS
  --cloud <provider>              Specify cloud provider (aws, gcp, azure, ali)
                                   QEMU VM: Ignores this flag

  --cloud-image                   Use an existing cloud image
                                   Possible images are listed on official releases

  --only-cleanup                  Only run $(tofu destroy) for cloud setups
                                   QEMU VM: Ignores this flag

  --image-requirements-file <file> Only needed with --cloud-image
                                   Needs to point to a valid *.requirements file

  --cloud-plan                    Only run 'tofu plan' for cloud setups
                                   QEMU VM: Ignores this flag

QEMU SPECIFIC OPTIONS
  --ssh                           Enable SSH access to QEMU VM (gardenlinux@127.0.0.1:2222)
                                   Cloud: SSHD is always enabled via cloud-init

ARTIFACT TYPES
  tar                             For chroot testing (extracted image filesystem)
  raw                             For QEMU VM testing or cloud provider testing

EXAMPLES
  # Run chroot tests on a tar image
  ./test-ng .build/aws-gardener_prod-amd64-today-13371337.tar

  # Run QEMU tests with SSH access and skip cleanup
  ./test-ng --ssh --skip-cleanup .build/aws-gardener_prod-amd64-today-13371337.raw

  # Run cloud tests on AWS, skipping cleanup
  ./test-ng --cloud aws --skip-cleanup .build/aws-gardener_prod-amd64-today-13371337.raw

  # Run cloud tests but skip test execution and cleanup
  ./test-ng --cloud aws --skip-tests --skip-cleanup .build/aws-gardener_prod-amd64-today-13371337.raw

  # Run QEMU tests and only run test_ssh.py in verbose mode
  ./test-ng --test-args "test_ssh.py -v" aws-gardener_prod-amd64-today-13371337.raw

  # Run cloud tests skip cleanup and only run specific tests in verbose mode
  ./test-ng --cloud aws --skip-cleanup --test-args "test_ssh.py test_aws.py -v" .build/aws-gardener_prod-amd64-today-13371337.raw

  # Spin up an existing cloud image using image requirements file
  ./test-ng --cloud aws --skip-cleanup --skip-tests --cloud-image --image-requirements-file .build/aws-gardener_prod-amd64-today-local.requirements ami-07f977508ed36098e

ENVIRONMENTS
  Chroot Testing: Runs tests directly in extracted image filesystem (fastest, filesystem-level only)
  QEMU Testing: Boots image in local QEMU virtual machine (full system testing, SSH on localhost:2222)
  Cloud Testing: Deploys image to cloud infrastructure using OpenTofu (real-world environment)

For more information, see tests-ng/README.md
EOF
}

cloud=

cloud_image=0
chroot_args=()
cloud_args=()
qemu_args=()

while [ $# -gt 0 ]; do
	case "$1" in
	# common
	--help)
		help
		exit 0
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
	# cloud specific
	--cloud)
		cloud="$2"
		shift 2
		;;
	--cloud-image)
		cloud_image=1
		shift
		;;
	--image-requirements-file)
		cloud_args+=("$1")
		cloud_args+=("$2")
		shift 2
		;;
	--cloud-plan)
		cloud_args+=("$1")
		shift
		;;
	# qemu specific
	--ssh)
		qemu_args+=("$1")
		shift
		;;
	*)
		break
		;;
	esac
done

# Check if artifact argument is provided
if [ $# -eq 0 ]; then
	echo "Error: No artifact specified" >&2
	echo "Use './test-ng --help' for usage information" >&2
	exit 1
fi

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
