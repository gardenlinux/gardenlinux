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

pwd
ls
cat $configFile

cd tests/
pipenv install
pytest --iaas=gcp --configfile=$configFile

echo "### DEBUG: success"
