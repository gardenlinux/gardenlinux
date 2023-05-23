#!/bin/bash
#set -Eeuo pipefail

# Name of Image to test
cname="${@: -1}"

configFile="azure_test_config.yaml"
containerName="ghcr.io/gardenlinux/gardenlinux/integration-test:today"
artifact_dir="/tmp/gardenlinux-build-artifacts"
platform_test_log_dir="/tmp/gardenlinux-platform-test-logs"

azure_hyper_v_generation="V1"
azure_vm_size="Standard_D4_v4"

mkdir -p "$platform_test_log_dir"

pushd "$artifact_dir" || exit 1
tar -xzf "$cname.tar.gz" "$cname.vhd"
du -bh "$cname.vhd"
du -h "$cname.vhd"
popd || exit 1

image_file=$(realpath "$artifact_dir/$cname.vhd")
echo "Image file that will be used for the tests is $image_file"
if [[ ! -e $image_file ]]; then
    echo "Image file $image_file does not exist."
    exit 1
fi

cat << EOF > "$configFile"
azure:
    location: westeurope
    subscription_id: ${azure_subscription_id}
    vm_size: ${azure_vm_size}
    hyper_v_generation: ${azure_hyper_v_generation}
    image: file:///artifacts/$(basename "$image_file")
    ssh:
      user: azureuser
    keep_running: false
    features:
      - azure
      - gardener
      - cloud
      - server
      - base
      - _slim
EOF

echo "### Start Integration Tests for Azure"
podman run -it --rm -v "${AZURE_CONFIG_DIR}:/root/.azure" -v "$(pwd):/gardenlinux" -v "$(dirname "$image_file"):/artifacts"  -v "$platform_test_log_dir:/platform-test-logs" $containerName /bin/bash -s << EOF
mkdir /gardenlinux/tmp
TMPDIR=/gardenlinux/tmp/
cd /gardenlinux/tests
pytest --iaas=azure --configfile=/gardenlinux/$configFile --junit-xml=/platform-test-logs/test-$cname-azure_junit.xml || exit 1
exit 0
EOF
