#!/usr/bin/env bash

set -euo pipefail

if [[ "$(docker images -q gardenlinux:build 2> /dev/null)" == "" ]]; then
	docker build -t gardenlinux:build .
fi

docker run --rm \
	--volume $(readlink -f packages):/packages \
	--volume $(readlink -f apt-remove-libdb.diff):/patch.diff \
	-e DEBFULLNAME="GardenLinux Maintainers" \
	-e DEBEMAIL="contact@gardenlinux.io" \
	-ti gardenlinux:build \
        bash -c "
		set -euo pipefail
		sudo apt-get update
		sudo apt-get build-dep -y --no-install-recommends apt-utils 
		sudo apt-get install -y --no-install-recommends devscripts # required for debuild
		apt-get source apt-utils 
		cd apt-*
		patch -p1 < /patch.diff
		dch -i 'remove ftparchive/libdb'
		debuild -b -uc -us
		sudo mv ../*.deb /packages
	"
