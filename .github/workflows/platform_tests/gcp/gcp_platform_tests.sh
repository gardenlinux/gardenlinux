#!/bin/bash

# Name of Image to test
image=$1
configFile=$(mktemp)

# generate yaml

cat << EOF > "$configFile"
gcp:
    project: ${gcp_project}
    region: ${gcp_region}
    zone: ${gcp_zone}
    image: ${image}
    ssh:
        user: gardenlinux
EOF

# TODO: call test with $configFile

echo "### DEBUG: success"
