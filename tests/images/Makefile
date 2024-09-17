VERSION=`../bin/garden-version`
ALTNAME=
ALTNAME_INTERNAL=$(shell [ -n "$(ALTNAME)" ] && printf "%s %s" "-t" "$(ALTNAME)" )

PATH_KERNEL_PACKAGES="../.packages/main/l/linux"
GARDENLINUX_BUILD_CRE ?= sudo podman

all: build-platform-test

.PHONY: needslim
needslim:
	@./needslim

.PHONY: build
build: needslim
	cp ../checksums.sha256 build/checksums.sha256
	@$(GARDENLINUX_BUILD_CRE) build --build-arg BUILDARCH="$$([ "$$(uname -m)" = "aarch64" ] && echo "arm64" || echo "amd64")" -t gardenlinux/build $(ALTNAME_INTERNAL) build
	rm build/checksums.sha256

.PHONY: build-base-test
build-base-test: needslim
	cp -p ../keyring.gpg base-test/keyring.gpg
	cp ../tests/Pipfile base-test/
	cp ../tests/Pipfile.lock base-test/
	@$(GARDENLINUX_BUILD_CRE) build --build-arg VERSION=$(VERSION) -t gardenlinux/base-test:$(VERSION) base-test
	rm base-test/keyring.gpg
	rm base-test/Pipfile
	rm base-test/Pipfile.lock

.PHONY: build-platform-test
build-platform-test: build-base-test
	cp ../checksums.sha256 platform-test/checksums.sha256
	@$(GARDENLINUX_BUILD_CRE) build --build-arg VERSION=$(VERSION) -t gardenlinux/platform-test:$(VERSION) platform-test
	rm platform-test/checksums.sha256

.PHONY: clean
clean:
	rm -rf platform-test/_pipfiles
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/platform-test --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/platform-test --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/slim --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/slim --format "{{.Repository}}:{{.Tag}}"); true
