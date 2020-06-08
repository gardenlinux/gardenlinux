#!/usr/bin/env bash

set -euo pipefail

# make sure the image we need is there, if not, build it
# TODO fix dockerfile path if run from somewhere else
if [[ "$(docker images -q reprepro:0.1 2> /dev/null)" == "" ]]; then
	docker build -t reprepro:0.1 . 
fi

# make sure the gpg agent is running
gpg-connect-agent /bye

# TODO clearsign something or make sure the TTL is large enough for the passphrase
# if the passphrase is not cached, the signing inside the container will fail because of
# pinentry permission issues

thisDir=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))
if GPG_KEY=$(grep ^SignWith "${thisDir}"/reprepro/reprepro/conf/distributions | awk '{ print $2 }' | head -1); then
	pubKey=$(gpg --armor --export "${GPG_KEY}") 
else	
	pubKey=""
fi
docker run --rm \
	--volume "$(gpgconf --list-dir agent-socket)":/root/.gnupg/S.gpg-agent \
	--volume "$(readlink -f reprepro)":/opt/reprepro \
	--volume "/home/admin/gardenlinux/repository":"/opt/reprepro/repository" \
	--volume "/home/admin/gardenlinux/packages":"/opt/reprepro/packages_gardenlinux" \
	-e GPG_TTY=/dev/console \
	-e GPG_KEY="${pubKey}" \
	-e ARGS="${*}" \
	-ti reprepro:0.1 \
        bash -c '
		echo "${GPG_KEY}" > /gpg-key
		gpg --import /gpg-key 2> /dev/null
		./opt/reprepro/repo.sh ${ARGS}' 

