POOLDIR=$(realpath ../.packages)
MANUALDIR=$(realpath manual)
KERNELDIR=$(realpath kernel)
CERTDIR=$(realpath ../cert)
DEBFULLNAME="Garden Linux Maintainers"
DEBEMAIL="contact@gardenlinux.io"
BUILDIMAGE="gardenlinux/build-deb"
BUILDKERNEL="gardenlinux/build-kernel"

.PHONY: all
all: pipeline

.PHONY: sign
sign:
	make --directory=../cert 

.PHONY: docker
docker:
	make --directory=../docker $$(basename $(BUILDIMAGE))

.PHONY: docker-kernel
docker-kernel:
	make --directory=../docker $$(basename $(BUILDKERNEL))

#--volume $(MANUALDIR)/../quiltrc:/home/dev/.quiltrc 
.PHONY: manual 
manual: docker sign
	docker run --rm -ti \
		--volume $(POOLDIR):/pool \
		--volume $(MANUALDIR):/home/dev/manual \
		--volume $(MANUALDIR)/../Makefile.inside:/home/dev/Makefile \
		--volume "$$(gpgconf --list-dir agent-socket)":/home/dev/.gnupg/S.gpg-agent \
		--volume $(CERTDIR)/sign.pub:/sign.pub \
		--volume $(CERTDIR)/Kernel.sign.full:/kernel.full \
		--volume $(CERTDIR)/Kernel.sign.crt:/kernel.crt \
		--volume $(CERTDIR)/Kernel.sign.key:/kernel.key \
	       	--env BUILDTARGET="/pool" \
		--env BUILDIMAGE=$(BUILDIMAGE) \
		--env DEBFULLNAME=$(DEBFULLNAME) \
		--env DEBEMAIL=$(DEBEMAIL) \
		--env WORKDIR="/home/dev" \
		$(BUILDIMAGE) bash -c "manual/.docker; bash"
.PHONY: pipeline 
pipeline: docker sign
	docker run --rm -ti \
		--volume $(POOLDIR):/pool \
		--volume $(MANUALDIR):/home/dev/manual \
		--volume $(MANUALDIR)/../Makefile.inside:/home/dev/Makefile \
		--volume "$$(gpgconf --list-dir agent-socket)":/home/dev/.gnupg/S.gpg-agent \
		--volume $(CERTDIR)/sign.pub:/sign.pub \
		--volume $(CERTDIR)/Kernel.sign.full:/kernel.full \
		--volume $(CERTDIR)/Kernel.sign.crt:/kernel.crt \
		--volume $(CERTDIR)/Kernel.sign.key:/kernel.key \
	       	--env BUILDTARGET="/pool" \
		--env BUILDIMAGE=$(BUILDIMAGE) \
		--env DEBFULLNAME=$(DEBFULLNAME) \
		--env DEBEMAIL=$(DEBEMAIL) \
		--env WORKDIR="/home/dev" \
		$(BUILDIMAGE) bash -c "gpg --import /sign.pub; make"
manual-kernel: docker-kernel
	docker run --rm -ti --volume "$(POOLDIR)":/pool --volume "$(KERNELDIR)":/home/dev/manual \
	       	--env BUILDTARGET="$(POOLDIR)" \
		--env BUILDIMAGE="$(BUILDKERNEL)" \
		--env DEBFULLNAME="$(DEBFULLNAME)" \
		--env DEBEMAIL="$(DEBEMAIL)" \
		--env WORKDIR="/home/dev" \
		$(BUILDKERNEL) bash -c " \
		set -euo pipefail \
		sudo apt-get install --no-install-recommends -y wget quilt vim less \
		\
		bash"
