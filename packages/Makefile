POOLDIR=$(realpath -e ../.packages)
MANUALDIR=$(realpath -e manual)
KERNELDIR=$(realpath -e kernel)
CERTDIR=$(realpath -e ../cert)
DEBFULLNAME="Garden Linux Maintainers"
DEBEMAIL="contact@gardenlinux.io"
BUILDIMAGE="gardenlinux/build-deb"
BUILDKERNEL="gardenlinux/build-kernel"

.PHONY: sign
sign:
	make --directory=../cert 

.PHONY: docker
docker:
	make --directory=../docker $$(basename $(BUILDIMAGE))

.PHONY: docker-kernel
docker-kernel:
	make --directory=../docker $$(basename $(BUILDKERNEL))

.PHONY: manual sign
manual: docker
	docker run --rm -ti \
		--volume $(POOLDIR):/pool \
		--volume $(MANUALDIR):/home/dev/manual \
		--volume $(MANUALDIR)/../Makefile.inside:/home/dev/Makefile \
		--volume $(MANUALDIR)/../quiltrc:/home/dev/.quiltrc \
		--volume "$$(gpgconf --list-dir agent-socket)":/home/dev/.gnupg/S.gpg-agent \
		--volume $(CERTDIR)/sign.pub:/sign.pub \
		--volume $(CERTDIR)/Kernel.sign.full:/kernel.crt \
		--volume $(CERTDIR)/Kernel.sign.key:/kernel.key \
	       	--env BUILDTARGET="/pool" \
		--env BUILDIMAGE=$(BUILDIMAGE) \
		--env DEBFULLNAME=$(DEBFULLNAME) \
		--env DEBEMAIL=$(DEBEMAIL) \
		$(BUILDIMAGE) bash -c "manual/.docker; bash"
manual-kernel: docker-kernel
	docker run --rm -ti --volume "$(POOLDIR)":/pool --volume "$(KERNELDIR)":/home/dev/manual \
	       	--env BUILDTARGET="$(POOLDIR)" \
		--env BUILDIMAGE="$(BUILDKERNEL)" \
		--env DEBFULLNAME="$(DEBFULLNAME)" \
		--env DEBEMAIL="$(DEBEMAIL)" \
		$(BUILDKERNEL) bash -c " \
		set -euo pipefail \
		sudo apt-get install --no-install-recommends -y wget quilt vim less \
		\
		bash"
