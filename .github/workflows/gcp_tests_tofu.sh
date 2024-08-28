#!/bin/bash
#set -Eeuo pipefail

# Name of Image to test
cname="${@: -1}"

configFile="gcp_test_config.yaml"
containerName="ghcr.io/gardenlinux/gardenlinux/platform-test:today"
artifact_dir="/tmp/gardenlinux-build-artifacts"
platform_test_log_dir="/tmp/gardenlinux-platform-test-logs"

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

if [ "$TARGET_ARCHITECTURE" == "arm64" ]; then
    machine_type="t2a-standard-2"
else
    machine_type="n1-standard-2"
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
tofu apply -auto-approve || tofu destroy -auto-approve

# Get public IP of the instance
public_ip="$(tofu output -raw public_ip)"

cat << EOF > "$configFile"
manual:
    host: ${public_ip}
    ssh:
        ssh_key_filepath: ~/.ssh/id_gardenlinux_test
        user: gardenlinux
    features:
      - gcp
      - gardener
      - cloud
      - server
      - base
      - _slim
EOF


echo "### Start Platform Tests for gcp"
podman run -it --rm -v "$(pwd):/gardenlinux" -v "$(dirname "$image_file"):/artifacts" -v "$platform_test_log_dir:/platform-test-logs" $containerName /bin/bash -s << EOF
mkdir /gardenlinux/tmp
TMPDIR=/gardenlinux/tmp/
cd /gardenlinux/tests
pytest --iaas=manual --configfile=/gardenlinux/$configFile --junit-xml=/platform-test-logs/test-$cname-gcp_junit.xml || exit 1
exit 0
EOF
