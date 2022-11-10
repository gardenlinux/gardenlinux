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

cat << EOF > "$configFile"
gcp:
    project: ${gcp_project}
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

credFileName=$(find "$(pwd)" -maxdepth 1 -type f -name "gha-creds-*.json" | xargs basename)

echo "### Start Integration Tests for gcp"
sudo podman run -it --rm  -v "$(pwd):/gardenlinux" -v "$(dirname "$image_file"):/artifacts" -v "$platform_test_log_dir:/platform-test-logs" $containerName /bin/bash -s << EOF
mkdir /gardenlinux/tmp
TMPDIR=/gardenlinux/tmp/
cd /gardenlinux/tests
export GOOGLE_APPLICATION_CREDENTIALS="/gardenlinux/$credFileName"
pytest --iaas=gcp --configfile=/gardenlinux/$configFile --junit-xml=/platform-test-logs/test-$prefix-gcp_junit.xml || exit 1
exit 0
EOF
