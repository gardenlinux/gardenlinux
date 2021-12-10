POOLDIR=$$(mkdir -p ../.packages; realpath ../.packages)
MANUALDIR=$(realpath manual)
KERNELDIR=$(realpath kernel)
BUILDLOGDIR=$$(mkdir -p ../.buildlogs; realpath ../.buildlogs)
CERTDIR=$(realpath ../cert)
PREDOWNLOADDIR=$(realpath downloads)
DEBFULLNAME="Garden Linux Maintainers"
DEBEMAIL="contact@gardenlinux.io"
BUILDIMAGE="gardenlinux/build-deb"
BUILDKERNEL="gardenlinux/build-kernel"
BUILDVERSION=$$(../bin/garden-version)
BUILDEPOCH=$$(../bin/garden-version --epoch)
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

.PHONY: download-linux-5.15
download-linux-5.15:
	rm -f $(MANUALDIR)/VERSION
	ln -s $(MANUALDIR)/linux.d/versions/VERSION-5.15 $(MANUALDIR)/VERSION
	./download-linux --output downloads --version $(MANUALDIR)/VERSION --base-dir $(MANUALDIR)/linux.d
.PHONY: download-linux-5.10
download-linux-5.10:
	rm -f $(MANUALDIR)/VERSION
	ln -s $(MANUALDIR)/linux.d/versions/VERSION-5.10 $(MANUALDIR)/VERSION
	./download-linux --output downloads --version $(MANUALDIR)/VERSION --base-dir $(MANUALDIR)/linux.d

.PHONY: download-linux-5.4
download-linux-5.4:
	rm -f $(MANUALDIR)/VERSION
	ln -s $(MANUALDIR)/linux.d/versions/VERSION-5.4 $(MANUALDIR)/VERSION
	./download-linux --output downloads --version $(MANUALDIR)/VERSION --base-dir $(MANUALDIR)/linux.d

.PHONY: manual-debug
manual-debug: docker sign
	docker run --rm -ti \
		--volume $(POOLDIR):/pool \
		--volume $(BUILDLOGDIR):/home/dev/buildlogs\
		--volume $(MANUALDIR):/home/dev/manual \
		--volume $(PREDOWNLOADDIR):/downloads \
		--volume $(MANUALDIR)/../Makefile.inside:/home/dev/Makefile \
		--volume "$$(gpgconf --list-dir agent-socket)":/home/dev/.gnupg/S.gpg-agent \
		--volume $(CERTDIR)/sign.pub:/sign.pub \
		--volume $(CERTDIR)/Kernel.sign.full:/kernel.full \
		--volume $(CERTDIR)/Kernel.sign.crt:/kernel.crt \
		--volume $(CERTDIR)/Kernel.sign.key:/kernel.key \
		 --tmpfs /tmp:exec,noatime \
	       	--env BUILDTARGET="/pool" \
		--env BUILDIMAGE=$(BUILDIMAGE) \
		--env BUILDVERSION=$(BUILDVERSION) \
		--env BUILDEPOCH=$(BUILDEPOCH) \
		--env DEBFULLNAME=$(DEBFULLNAME) \
		--env DEBEMAIL=$(DEBEMAIL) \
		--env WORKDIR="/home/dev" \
		$(BUILDIMAGE) bash -c "manual/.docker; bash"

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
		 --tmpfs /tmp:exec,noatime \
	       	--env BUILDTARGET="/pool" \
		--env BUILDIMAGE=$(BUILDIMAGE) \
		--env BUILDVERSION=$(BUILDVERSION) \
		--env BUILDEPOCH=$(BUILDEPOCH) \
		--env DEBFULLNAME=$(DEBFULLNAME) \
		--env DEBEMAIL=$(DEBEMAIL) \
		--env WORKDIR="/home/dev" \
		$(BUILDIMAGE) bash -c "manual/.docker; bash"

.PHONY: manual-kernel
manual-kernel: docker-kernel
	docker run --rm -ti \
		--volume "$(POOLDIR)":/pool \
		--volume "$(KERNELDIR)":/home/dev/manual \
	       	--env BUILDTARGET=$(POOLDIR) \
		--env BUILDIMAGE=$(BUILDKERNEL) \
		--env BUILDVERSION=$(BUILDVERSION) \
		--env BUILDEPOCH=$(BUILDEPOCH) \
		--env DEBFULLNAME=$(DEBFULLNAME) \
		--env DEBEMAIL=$(DEBEMAIL) \
		--env WORKDIR="/home/dev" \
		$(BUILDKERNEL) bash

.PHONY: pipeline
pipeline: docker sign
	docker run --rm \
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
		--env BUILDVERSION=$(BUILDVERSION) \
		--env BUILDEPOCH=$(BUILDEPOCH) \
		--env DEBFULLNAME=$(DEBFULLNAME) \
		--env DEBEMAIL=$(DEBEMAIL) \
		--env WORKDIR="/home/dev" \
		$(BUILDIMAGE) bash -c "gpg --import /sign.pub; make"
