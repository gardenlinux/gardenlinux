#!/bin/bash
#set -Eeuo pipefail

# Name of Image to test
image=$1

configFile="gcp_config"
containerName="ghcr.io/gardenlinux/gardenlinux/integration-test:today"

cat << EOF > "$configFile"
gcp:
    project: ${gcp_project}
    region: ${gcp_region}
    zone: ${gcp_zone}
    image: file:///gardenlinux/.build/${image}
    ssh:
        user: gardenlinux
EOF

mkdir -p .build
mv $image .build/

credFileName=$(find "`pwd`" -maxdepth 1 -type f -name "gha-creds-*.json" | xargs basename)

echo "### Start Integration Tests for gcp"
sudo podman run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build $containerName /bin/bash -s <<EOF
mkdir /gardenlinux/tmp
TMPDIR=/gardenlinux/tmp/
cd /gardenlinux
export GOOGLE_APPLICATION_CREDENTIALS="/gardenlinux/$credFileName"
pytest --iaas=gcp --configfile=/gardenlinux/$configFile || exit 1
EOF

#gcloud auth application-default login --client-id-file="/gardenlinux/$credFileName" || exit 1
#gcloud config set project ${gcp_project}
