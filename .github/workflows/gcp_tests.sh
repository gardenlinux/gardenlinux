#!/bin/bash
#set -Eeuo pipefail

# Name of Image to test
image="${@: -1}"

configFile="gcp_test_config.yaml"
containerName="ghcr.io/gardenlinux/gardenlinux/integration-test:today"
artifact_dir="/tmp/gardenlinux-build-artifacts"
platform_test_log_dir="/tmp/gardenlinux-platform-test-logs"

mkdir -p "$platform_test_log_dir"

pushd "$artifact_dir" || exit 1
artifact=$(find . -maxdepth 1 -type f -name "$image")
echo "Extracting $artifact..."
tar -xzf "$artifact"
subdir=$(find . -maxdepth 1 ! -path . -type d)
echo "Artifacts extracted to $subdir"
prefix="$(sed 's#^/##' "$subdir/prefix.info")"
popd || exit 1

image_file=$(realpath "$artifact_dir/$subdir/$prefix.tar.gz")
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

cat << EOF > "$configFile"
gcp:
    project: ${gcp_project}
    service_account_json_path: "/gardenlinux/$credentials_file_name"
    region: ${gcp_region}
    zone: ${gcp_zone}
    image: file:///artifacts/$(basename "$image_file")
    ssh:
        user: gardenlinux
    features:
      - gcp
      - gardener
      - cloud
      - server
      - base
      - _slim
EOF


echo "### Start Integration Tests for gcp"
sudo podman run -it --rm  -v "$(pwd):/gardenlinux" -v "$(dirname "$image_file"):/artifacts" -v "$platform_test_log_dir:/platform-test-logs" $containerName /bin/bash -s << EOF
mkdir /gardenlinux/tmp
TMPDIR=/gardenlinux/tmp/
cd /gardenlinux/tests
export GOOGLE_APPLICATION_CREDENTIALS="/gardenlinux/$credentials_file_name"
pytest --iaas=gcp --configfile=/gardenlinux/$configFile --junit-xml=/platform-test-logs/test-$prefix-gcp_junit.xml || exit 1
exit 0
EOF


