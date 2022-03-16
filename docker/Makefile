VERSION=`../bin/garden-version`
ALTNAME=
ALTNAME_INTERNAL=$(shell [ -n "$(ALTNAME)" ] && printf "%s %s" "-t" "$(ALTNAME)" ) 

PATH_KERNEL_PACKAGES="../.packages/main/l/linux"
KERNEL_VERSION=5.10

all: build-image build-integration-test

.PHONY: needslim
needslim:
	@./needslim

.PHONY: build-image
build-image: needslim
	cp ../bin/garden-feat.go build-image/
	@sudo podman build --build-arg VERSION=$(VERSION) -t gardenlinux/build-image:$(VERSION) $(ALTNAME_INTERNAL) build-image

.PHONY: build
build: needslim
	@sudo podman build --build-arg BUILDARCH="$$([ "$$(uname -m)" = "aarch64" ] && echo "arm64" || echo "amd64")" -t gardenlinux/build $(ALTNAME_INTERNAL) build

.PHONY: build-deb
build-deb: build
	@sudo podman build -t gardenlinux/build-deb $(ALTNAME_INTERNAL) build-deb

.PHONY: build-integration-test
build-integration-test: needslim
	mkdir -p integration-test/_pipfiles
	cp ../tests/Pipfile* integration-test/_pipfiles
	@sudo podman build -t gardenlinux/integration-test:$(VERSION) integration-test

.PHONY: build-kernelmodule
build-kernelmodule: build
	rm -rf build-kernelmodule/packages
	mkdir -p build-kernelmodule/packages/
	cp ../.packages/main/l/linux/linux-kbuild*$(KERNEL_VERSION)*.deb build-kernelmodule/packages/ || (echo "Error: Build Kernel packages first." && exit 1)
	cp ../.packages/main/l/linux/linux-compiler-gcc*$(KERNEL_VERSION)*.deb build-kernelmodule/packages/ || (echo "Error: Build Kernel packages first." && exit 1)
	cp ../.packages/main/l/linux/linux-headers*$(KERNEL_VERSION)*.deb build-kernelmodule/packages/ || (echo "Error: Build Kernel packages first." && exit 1)
	@sudo podman build -t gardenlinux/build-kernelmodule:$(KERNEL_VERSION) build-kernelmodule

.PHONY: clean
clean:
	rm -rf integration-test/_pipfiles
	-@[ -n "$$(sudo podman image ls gardenlinux/integration-test --format "{{.ID}}")" ] && sudo podman image rm --force $$(sudo podman image ls gardenlinux/integration-test --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(sudo podman image ls gardenlinux/build-image --format "{{.ID}}")" ] && sudo podman image rm --force $$(sudo podman image ls gardenlinux/build-image --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(sudo podman image ls gardenlinux/build-deb --format "{{.ID}}")" ] && sudo podman image rm --force $$(sudo podman image ls gardenlinux/build-deb --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(sudo podman image ls gardenlinux/build --format "{{.ID}}")" ] && sudo podman image rm --force $$(sudo podman image ls gardenlinux/build --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(sudo podman image ls gardenlinux/slim --format "{{.ID}}")" ] && sudo podman image rm --force $$(sudo podman image ls gardenlinux/slim --format "{{.Repository}}:{{.Tag}}"); true
