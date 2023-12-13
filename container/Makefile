VERSION=`../bin/garden-version`
ALTNAME=
ALTNAME_INTERNAL=$(shell [ -n "$(ALTNAME)" ] && printf "%s %s" "-t" "$(ALTNAME)" )

PATH_KERNEL_PACKAGES="../.packages/main/l/linux"
GARDENLINUX_BUILD_CRE ?= sudo podman

all: build-integration-test

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
	cp -p ../gardenlinux.asc base-test/gardenlinux.asc
	cp ../tests/Pipfile base-test/
	cp ../tests/Pipfile.lock base-test/
	@$(GARDENLINUX_BUILD_CRE) build --build-arg VERSION=$(VERSION) -t gardenlinux/base-test:$(VERSION) base-test
	rm base-test/gardenlinux.asc
	rm base-test/Pipfile

.PHONY: build-integration-test
build-integration-test: build-base-test
	cp ../checksums.sha256 integration-test/checksums.sha256
	cat integration-test/cloud.google.gpg.base64 | base64 -d > integration-test/cloud.google.gpg
	@$(GARDENLINUX_BUILD_CRE) build --build-arg VERSION=$(VERSION) -t gardenlinux/integration-test:$(VERSION) integration-test
	rm integration-test/checksums.sha256
	rm integration-test/cloud.google.gpg

.PHONY: clean
clean:
	rm -rf integration-test/_pipfiles
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/integration-test --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/integration-test --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/slim --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/slim --format "{{.Repository}}:{{.Tag}}"); true
