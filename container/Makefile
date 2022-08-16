VERSION=`../bin/garden-version`
VERSION_NUMBER_MAJOR=$(shell ../bin/garden-version --major)
VERSION_NUMBER_MINOR=$(shell ../bin/garden-version --minor)
VERSION_NUMBER=$(VERSION_NUMBER_MAJOR).$(VERSION_NUMBER_MINOR)
ALTNAME=
ALTNAME_INTERNAL=$(shell [ -n "$(ALTNAME)" ] && printf "%s %s" "-t" "$(ALTNAME)" )

PATH_KERNEL_PACKAGES="../.packages/main/l/linux"
KERNEL_VERSION=`../bin/garden-version --kernel`

GARDENLINUX_BUILD_CRE ?= sudo podman

all: build-image build-cert build-integration-test

.PHONY: needslim
needslim:
	@./needslim

.PHONY: build-image
build-image: needslim
	cp ../bin/garden-feat.go build-image/
	if [ ! -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build-image:$(VERSION_NUMBER) --format "{{.Repository}}:{{.Tag}}")" ]; then \
		$(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build-image --format "{{.Repository}}:{{.Tag}}") || true; \
	fi
	@$(GARDENLINUX_BUILD_CRE) build --build-arg VERSION=$(VERSION) -t gardenlinux/build-image:$(VERSION) -t gardenlinux/build-image:$(VERSION_NUMBER) $(ALTNAME_INTERNAL) build-image; \

.PHONY: build-cert
build-cert: needslim
	@$(GARDENLINUX_BUILD_CRE) build --build-arg VERSION=$(VERSION) -t gardenlinux/build-cert:$(VERSION) $(ALTNAME_INTERNAL) build-cert

.PHONY: build
build: needslim
	@$(GARDENLINUX_BUILD_CRE) build --build-arg BUILDARCH="$$([ "$$(uname -m)" = "aarch64" ] && echo "arm64" || echo "amd64")" -t gardenlinux/build $(ALTNAME_INTERNAL) build

.PHONY: build-deb
build-deb: build
	@$(GARDENLINUX_BUILD_CRE) build -t gardenlinux/build-deb $(ALTNAME_INTERNAL) build-deb

.PHONY: build-base-test
build-base-test: needslim
	mkdir -p base-test/_pipfiles
	cp ../tests/Pipfile* base-test/_pipfiles
	@$(GARDENLINUX_BUILD_CRE) build -t gardenlinux/base-test:$(VERSION) base-test

.PHONY: build-integration-test
build-integration-test: build-base-test
	mkdir -p integration-test/_pipfiles
	cp ../tests/Pipfile* integration-test/_pipfiles
	@$(GARDENLINUX_BUILD_CRE) build --build-arg VERSION=$(VERSION) -t gardenlinux/integration-test:$(VERSION) integration-test

.PHONY: kernelmodule-builder-arm64
kernelmodule-builder-arm64:
	cp ../gardenlinux.asc kernelmodule-builder
	@$(GARDENLINUX_BUILD_CRE) build --build-arg KERNEL_VERSION=$(KERNEL_VERSION) --build-arg TARGET_ARCH="arm64" --build-arg GNU_TYPE_PACKAGE="aarch64-linux-gnu" --build-arg GLSUITE=$(VERSION) -t gardenlinux/build-kernelmodule:$(VERSION) kernelmodule-builder

.PHONY: kernelmodule-builder-amd64
kernelmodule-builder-amd64:
	cp ../gardenlinux.asc kernelmodule-builder
	@$(GARDENLINUX_BUILD_CRE) build --build-arg KERNEL_VERSION=$(KERNEL_VERSION) --build-arg TARGET_ARCH="amd64" --build-arg GNU_TYPE_PACKAGE="x86-64-linux-gnu" --build-arg GLSUITE=$(VERSION) -t gardenlinux/build-kernelmodule:$(VERSION) kernelmodule-builder

.PHONY: clean
clean:
	rm -rf integration-test/_pipfiles
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/integration-test --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/integration-test --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build-image --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build-image --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build-deb --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build-deb --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/build --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/slim --format "{{.ID}}")" ] && $(GARDENLINUX_BUILD_CRE) image rm --force $$($(GARDENLINUX_BUILD_CRE) image ls gardenlinux/slim --format "{{.Repository}}:{{.Tag}}"); true
