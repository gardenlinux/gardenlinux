#!/bin/bash
#set -Eeuo pipefail

# Name of Image to test
cname="${@: -1}"

configFile="ali_test_config.yaml"
containerName="ghcr.io/gardenlinux/gardenlinux/integration-test:today"
artifact_dir="/tmp/gardenlinux-build-artifacts"
platform_test_log_dir="/tmp/gardenlinux-platform-test-logs"

mkdir -p "$platform_test_log_dir"

pushd "$artifact_dir" || exit 1
tar -xzf "$cname.tar.gz" "$cname.qcow2"
popd || exit 1

image_file=$(realpath "$artifact_dir/$cname.qcow2")
echo "Image file that will be used for the tests is $image_file"
if [[ ! -e $image_file ]]; then
    echo "Image file $image_file does not exist."
    exit 1
fi

cat << EOF > "$configFile"
ali:
    test_name: gl-selinux-credativ
    credential_file: /gardenlinux/ali-service-account.json
    image: file:///artifacts/$(basename "$image_file")
    instance_type: ecs.t6-c1m2.large
    security_group_id: sg-gw8clj5rau3bazvoxxlu
    vswitch_id: vsw-gw8itw7yozjthfek7xgel
    region_id: eu-central-1
    zone_id: eu-central-1a
    bucket: develop-gardener
    ssh:
      ssh_key_filepath: /gardenlinux/tmp/id_rsa
      key_name: gardenlinux-test
      user: admin
    keep_running: false
    features:
    - ali
    - gardener
    - cloud
    - server
    - base
    - _slim
EOF


echo "### Start Integration Tests for ali"
podman run -it --rm -v "$(pwd):/gardenlinux" -v "$(dirname "$image_file"):/artifacts" -v "$platform_test_log_dir:/platform-test-logs" $containerName /bin/bash -s << EOF
mkdir /gardenlinux/tmp
TMPDIR=/gardenlinux/tmp/
ssh-keygen -t rsa -b 4096 -f /gardenlinux/tmp/id_rsa -N "" -q
cd /gardenlinux/tests
pytest --iaas=ali --configfile=/gardenlinux/$configFile --junit-xml=/platform-test-logs/test-$cname-ali_junit.xml || exit 1
exit 0
EOF
