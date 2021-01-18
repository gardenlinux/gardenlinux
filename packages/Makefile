POOLDIR=$(readlink -f ../.packages)
MANUALDIR=$(realink -f manual)
BUILDNAME="Garden Linux Maintainers"
BUILDEMAIL="contact@gardenlinux.io"
BUILDIMAGE="gardenlinux/build-deb"

.PHONY: docker
docker:
	make -C ../docker $$(basename $(BUILDIMAGE))

.PHONY: manual
manual: docker
	docker run --rm -ti --volume "$(POOLDIR)":/pool --volume "$(MANUALDIR)":/home/dev/manual \
	       	--env BUILDTARGET="$(POOLDIR)" \
		--env BUILDIMAGE="$(BUILDIMAGE)" \
		--env DEBFULLNAME="$(BUILDNAME)" \
		--env DEBEMAIL="$(BUILDEMAIL)" \
		$(BUILDIMAGE) bash -c " \
		set -euo pipefail \
		sudo apt-get install --no-install-recommends -y wget quilt vim less \
		\
		bash"

