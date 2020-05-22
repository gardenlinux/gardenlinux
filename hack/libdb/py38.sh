#!/usr/bin/env bash

set -euo pipefail

if [[ "$(docker images -q gardenlinux:build 2> /dev/null)" == "" ]]; then
	docker build -t gardenlinux:build .
fi

docker run --rm \
	--volume $(readlink -f packages):/packages \
	--volume $(readlink -f py38-remove-libdb.diff):/patch.diff \
	-e DEBFULLNAME="GardenLinux Maintainers" \
	-e DEBEMAIL="contact@gardenlinux.io" \
	-ti gardenlinux:build \
        bash -c "
		set -euo pipefail
		sudo apt-get update
		sudo apt-get build-dep -y --no-install-recommends python3.8
		sudo apt-get install -y --no-install-recommends devscripts # required for debuild
		apt-get source python3.8
		cd python3.8-*
		patch -p1 < /patch.diff
		dch -i 'remove libdb'
		sudo apt-get remove -y --purge libdb5.3-dev
		debuild -b -uc -us
		mv ../*.deb /packages
	"
