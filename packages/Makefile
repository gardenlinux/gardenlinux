POOLDIR=$$(mkdir -p ../.packages; realpath ../.packages)
MANUALDIR=$(realpath manual)
KERNELDIR=$(realpath kernel)
CERTDIR=$(realpath ../cert)
DEBFULLNAME="Garden Linux Maintainers"
DEBEMAIL="contact@gardenlinux.io"
ARCH ?= $(shell [ "$$(uname -m)" = "aarch64" ] && echo "arm64" || echo "amd64")
BUILDIMAGE="gardenlinux/build-deb-$(ARCH)"
BUILDVERSION=$$(../bin/garden-version)
BUILDEPOCH=$$(../bin/garden-version --epoch)

PACKAGES=apt cyrus-sasl2 dracut iproute2 pam python3.9 linux-5.10 linux-5.10-signed selinux-basics waagent google-compute-engine google-compute-engine-oslogin google-guest-agent
.PHONY: $(PACKAGES)

.PHONY: all
all: $(PACKAGES)

.PHONY: sign
sign:
	make --directory=../cert

.PHONY: docker
docker:
	make --directory=../docker ARCH=$(ARCH) build-deb

.PHONY: docker-kernel
docker-kernel:
	make --directory=../docker $$(basename $(BUILDKERNEL))

linux-5.10-signed: linux-5.10

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
$(PACKAGES): docker sign
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
		$(BUILDIMAGE) bash -c "gpg --import /sign.pub; make $@"
manual-kernel: docker-kernel
	docker run --rm --volume "$(POOLDIR)":/pool --volume "$(KERNELDIR)":/home/dev/manual \
		--env BUILDTARGET="$(POOLDIR)" \
		--env BUILDIMAGE="$(BUILDKERNEL)" \
		--env BUILDVERSION=$(BUILDVERSION) \
		--env BUILDEPOCH=$(BUILDEPOCH) \
		--env DEBFULLNAME="$(DEBFULLNAME)" \
		--env DEBEMAIL="$(DEBEMAIL)" \
		--env WORKDIR="/home/dev" \
		$(BUILDKERNEL) bash -c " \
		set -euo pipefail \
		sudo apt-get install --no-install-recommends -y wget quilt vim less \
		\
		bash"
