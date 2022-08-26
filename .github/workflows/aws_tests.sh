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
image=$1

configFile="gcp_config"
containerName="ghcr.io/gardenlinux/gardenlinux/integration-test:today"
artifact_dir="/tmp/gardenlinux-build-artifacts"

pushd "$artifact_dir" || exit 1
artifact=$(find . -maxdepth 1 -type f -name "$image")
echo "Extracting $artifact..."
tar -xzf "$artifact"
subdir=$(find . -maxdepth 1 ! -path . -type d)
echo "Artifacts extracted to $subdir"
prefix="$(sed 's#^/##' "$subdir/prefix.info")"
popd || exit 1

image_file=$(realpath "$artifact_dir/$subdir/$prefix.raw")
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
    keep_running: false
EOF

echo "### Start Integration Tests for AWS"
env_list="$(env | cut -d = -f 1 | grep '^AWS_' | tr '\n' ',' | sed 's/,$//')"
sudo --preserve-env="$env_list" podman run -it --rm -e 'AWS_*' -v "$(pwd):/gardenlinux" -v "$(dirname "$image_file"):/artifacts" $containerName /bin/bash -s << EOF
mkdir /gardenlinux/tmp
TMPDIR=/gardenlinux/tmp/
cd /gardenlinux/tests
pytest --iaas=aws --configfile=/gardenlinux/$configFile --junit-xml=/gardenlinux/test-$prefix-aws.xml integration || exit 1
exit 0
EOF
