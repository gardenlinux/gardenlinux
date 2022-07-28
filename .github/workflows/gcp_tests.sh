#!/bin/bash
set -Eeuo pipefail

# Name of Image to test
image=$1


configFile=$(mktemp)
containerName="ghcr.io/gardenlinux/gardenlinux/integration-test:today"

cat << EOF > "$configFile"
gcp:
    project: ${gcp_project}
    region: ${gcp_region}
    zone: ${gcp_zone}
    image: ${image}
    ssh:
        user: gardenlinux
EOF

mkdir -p .build
mv $image .build/

echo "### Start Integration Tests for gcp"
sudo podman run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.config:/root/.config -v $HOME/config:/config $containerName /bin/bash -s <<EOF
pytest --iaas=gcp --configfile=$configFile
EOF

