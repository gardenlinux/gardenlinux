#!/usr/bin/env bash

set -euo pipefail

if [[ "$(docker images -q gardenlinux:build 2> /dev/null)" == "" ]]; then
	docker build -t gardenlinux:build .
fi

docker run --rm \
	--volume $(readlink -f packages):/packages \
	--volume $(readlink -f py27-remove-libdb.diff):/patch.diff \
	-e DEBFULLNAME="GardenLinux Maintainers" \
	-e DEBEMAIL="contact@gardenlinux.io" \
	-ti gardenlinux:build \
        bash -c "
		set -euo pipefail
		sudo apt-get update
		sudo apt-get build-dep -y --no-install-recommends python2.7
		sudo apt-get install -y --no-install-recommends devscripts # required for debuild
		sudo apt-get install -y libgdbm-compat-dev
		apt-get source python2.7
		cd python2.7-*
		patch -p1 < /patch.diff
		dch -i 'remove _bsddb module'
		sudo apt-get remove -y --purge libdb-dev libdb5.3-dev
		debuild -b -uc -us
		sudo mv ../*.deb /packages
	"
