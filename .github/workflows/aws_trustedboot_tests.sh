#!/bin/bash
#set -Eeuo pipefail

arch=amd64

while [ $# -gt 0 ]; do
  case "$1" in
    --arch)
      arch="$2"
      shift 2
      ;;
    *)
      break
      ;;
  esac
done

# Name of Image to test
cname=$1

configFile="aws_test_config.yaml"
containerName="ghcr.io/gardenlinux/gardenlinux/platform-test:today"
artifact_dir="/tmp/gardenlinux-build-artifacts"

junit_suite_name="${0/.sh/}"

pushd "$artifact_dir" || exit 1
test -f "$cname.raw" || tar -xzf "$cname.tar.gz" "$cname.raw"
popd || exit 1

image_file=$(realpath "$artifact_dir/$cname.raw")
echo "Image file that will be used for the tests is $image_file"
if [[ ! -e $image_file ]]; then
    echo "Image file $image_file does not exist."
    exit 1
fi

case "$arch" in
  amd64) instance_type=m5.large ;;
  arm64) instance_type=m6g.large ;;
  *)
    echo "unsupported architecture $arch" >&2
    exit 1
    ;;
esac

cat << EOF > "$configFile"
aws:
    region: ${aws_region}
    instance_type: $instance_type
    architecture: $arch
    image: file:///artifacts/$(basename "$image_file")
    ssh:
      user: admin
    boot_mode: uefi
    uefi_data: '$(cat cert/gardenlinux-secureboot.aws-efivars)'
    keep_running: false
    features:
      - aws
      - gardener
      - cloud
      - server
      - base
      - _slim
      - _trustedboot
EOF

echo "### Start Integration Tests for AWS"
podman run -it --rm -e 'AWS_*' -v "$(pwd):/gardenlinux" -v "$(dirname "$image_file"):/artifacts" $containerName /bin/bash -s << EOF
mkdir /gardenlinux/tmp
TMPDIR=/gardenlinux/tmp/
cd /gardenlinux/tests
pytest --iaas=aws --configfile=/gardenlinux/$configFile --junit-xml=/artifacts/$cname.platform.test.xml -o junit_suite_name=$junit_suite_name || exit 1
exit 0
EOF
