VERSION=`../bin/garden-version`
ALTNAME=

ALTNAME_INTERNAL=$(shell [ -n "$(ALTNAME)" ] && printf "%s %s" "-t" "$(ALTNAME)" )

ARCH ?= $(shell [ "$$(uname -m)" = "aarch64" ] && echo "arm64" || echo "amd64")

all: build-image build-integration-test

.PHONY: needslim
needslim:
	@./needslim

.PHONY: build-image
build-image: needslim
	cp ../bin/garden-feat.go build-image/
	@docker build --build-arg VERSION=$(VERSION) -t gardenlinux/build-image:$(VERSION) $(ALTNAME_INTERNAL) build-image

.PHONY: build-deb
build-deb: needslim
	@docker build --build-arg ARCH=$(ARCH) -t gardenlinux/build-deb-$(ARCH) $(ALTNAME_INTERNAL) build-deb

.PHONY: build-integration-test
build-integration-test: needslim
	mkdir -p integration-test/_pipfiles
	cp ../tests/Pipfile* integration-test/_pipfiles
	@docker build -t gardenlinux/integration-test:$(VERSION) integration-test

.PHONY: clean
clean:
	rm -rf integration-test/_pipfiles
	-@[ -n "$$(docker image ls gardenlinux/integration-test --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/integration-test --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(docker image ls gardenlinux/build-image --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/build-image --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(docker image ls gardenlinux/build-deb-$(ARCH) --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/build-deb-$(ARCH) --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(docker image ls gardenlinux/slim --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/slim --format "{{.Repository}}:{{.Tag}}"); true
