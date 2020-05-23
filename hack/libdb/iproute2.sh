#!/usr/bin/env bash

set -euo pipefail

if [[ "$(docker images -q gardenlinux:build 2> /dev/null)" == "" ]]; then
	docker build -t gardenlinux:build .
fi

docker run \
	--volume $(readlink -f packages):/packages \
	--volume $(readlink -f iproute2.diff):/patch.diff \
	-e DEBFULLNAME="GardenLinux Maintainers" \
	-e DEBEMAIL="contact@gardenlinux.io" \
	-ti gardenlinux:build \
        bash -c "
		set -euo pipefail
		sudo apt-get update
		sudo apt-get build-dep -y --no-install-recommends iproute2
		sudo apt-get install -y --no-install-recommends devscripts # required for debuild
		apt-get source iproute2
		cd iproute2-*
		patch -p1 < /patch.diff
		dch -i 'remove libdb'
		sudo apt-get remove -y --purge libdb5.3-dev
		dpkg-buildpackages
		sudo mv ../*.deb /packages
	"
