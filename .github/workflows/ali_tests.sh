#!/bin/bash
#set -Eeuo pipefail

# Name of Image to test
cname="${@: -1}"

configFile="ali_test_config.yaml"
containerName="ghcr.io/gardenlinux/gardenlinux/integration-test:today"
artifact_dir="/tmp/gardenlinux-build-artifacts"

if [ -f ".build/${cname}.qcow2" ]; then
    mkdir -p "${artifact_dir}"
    cp .build/* "${artifact_dir}"
else
    pushd "$artifact_dir" || exit 1
    tar -xzf "$cname.tar.gz" "$cname.qcow2"
    popd || exit 1
fi

if [ -f "/gardenlinux/ali-service-account.json" ]; then
    jq -r --arg 'access_key_id' "${ALIBABA_CLOUD_ACCESS_KEY_ID}" --arg 'access_key_secret' "${ALIBABA_CLOUD_ACCESS_KEY_SECRET}" --arg 'region' "${ALIBABA_CLOUD_REGION}" -n '{
        "current": "gardenlinux",
        "profiles": [
            {
                "name": "gardenlinux",
                "mode": "AK",
                "access_key_id": $access_key_id,
                "access_key_secret": $access_key_secret,
                "sts_token": "",
                "ram_role_name": "",
                "ram_role_arn": "",
                "ram_session_name": "",
                "private_key": "",
                "key_pair_name": "",
                "expired_seconds": 0,
                "verified": "",
                "region_id": $region,
                "output_format": "json",
                "language": "en",
                "site": "",
                "retry_timeout": 0,
                "connect_timeout": 0,
                "retry_count": 0,
                "process_command": ""
            }
        ],
        "meta_path": ""
    }' '.' > /gardenlinux/ali-service-account.json
fi

image_file=$(realpath "$artifact_dir/$cname.qcow2")
echo "Image file that will be used for the tests is $image_file"
if [[ ! -e $image_file ]]; then
    echo "Image file $image_file does not exist."
    exit 1
fi

cat << EOF > "$configFile"
ali:
    credential_file: /gardenlinux/ali-service-account.json
    image: file:///artifacts/$(basename "$image_file")
    instance_type: ecs.t6-c1m2.large
    security_group_id: sg-gw8clj5rau3bazvoxxlu
    vswitch_id: vsw-gw8itw7yozjthfek7xgel
    region_id: eu-central-1
    zone_id: eu-central-1a
    bucket: gardenlinux-test-upload
    ssh:
      ssh_key_filepath: /gardenlinux/tmp/id_rsa
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
podman run -it --rm -v "$(pwd):/gardenlinux" -v "$(dirname "$image_file"):/artifacts" $containerName /bin/bash -s << EOF
mkdir /gardenlinux/tmp
TMPDIR=/gardenlinux/tmp/
ssh-keygen -t rsa -b 4096 -f /gardenlinux/tmp/id_rsa -N "" -q
cd /gardenlinux/tests
pytest --iaas=ali --configfile=/gardenlinux/$configFile --junit-xml=/artifacts/$cname.platform.test.xml || exit 1
exit 0
EOF
