#!/bin/bash
#set -Eeuo pipefail

# Name of Image to test
cname="${@: -1}"

configFile="gcp_test_config.yaml"
containerName="ghcr.io/gardenlinux/gardenlinux/platform-test:today"
artifact_dir="/tmp/gardenlinux-build-artifacts"
platform_test_log_dir="/tmp/gardenlinux-platform-test-cleanup-logs"

mkdir -p "$platform_test_log_dir"

pushd "$artifact_dir" || exit 1
tar -xzf "$cname.tar.gz" "$cname.gcpimage.tar.gz"
popd || exit 1

image_file=$(realpath "$artifact_dir/$cname.gcpimage.tar.gz")
echo "Image file that will be used for the tests is $image_file"
if [[ ! -e $image_file ]]; then
    echo "Image file $image_file does not exist."
    exit 1
fi

if [[ ! ${gcp_project:-} ]]; then
    echo "gcp_project variable not set"
    exit 1
fi

if [[ ! ${gcp_region:-} ]]; then
    echo "gcp_project variable not set"
    exit 1
fi

if [[ ! ${gcp_zone:-} ]]; then
    echo "gcp_project variable not set"
    exit 1
fi

# Note: file is located in github runner within checked out repo.
#        later, we mount the repo folder to /gardenlinux inside the container.
#        google-githun-actions/auth cleans up credential file. We just take the name,
#        to reference it inside the container
if [[ ! ${GOOGLE_APPLICATION_CREDENTIALS:-} ]]; then
    echo "GOOGLE_APPLICATION_CREDENTIALS not set by google-github-actions/auth action."
    exit 1
fi

credentials_file_name="$(echo "$GOOGLE_APPLICATION_CREDENTIALS" | xargs basename)"

# OpenTofu configuration
cat << EOF > "$tfFile"
project_id     = "${gcp_project}"
region         = "${gcp_region}"
region_storage = "${gcp_region}"
test_name      = "c5227532-tf-test-workflow"
image_source   = "/artifacts/$(basename "$image_file")
ssh_public_key = "~/.ssh/id_gardenlinux_test.pub"
EOF

# OpenTofu apply and destroy if failed
cd tests/platformSetup/tofu/gcp
tofu destroy -auto-approve
