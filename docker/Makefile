VERSION=`../bin/garden-version`
ALTNAME=

ALTNAME_INTERNAL=$(shell [ -n "$(ALTNAME)" ] && printf "%s %s" "-t" "$(ALTNAME)" ) 

all: build-image build-integration-test

.PHONY: needslim
needslim:
	@./needslim

.PHONY: build-image
build-image: needslim
	@docker build --build-arg VERSION=$(VERSION) -t gardenlinux/build-image:$(VERSION) $(ALTNAME_INTERNAL) build-image

.PHONY: build
build: needslim
	@docker build --build-arg BUILDARCH="$$(dpkg --print-architecture | awk -F- "{ print \$$NF }")" -t gardenlinux/build $(ALTNAME_INTERNAL) build

.PHONY: build-deb
build-deb: build
	@docker build -t gardenlinux/build-deb $(ALTNAME_INTERNAL) build-deb

.PHONY: build-integration-test
build-integration-test:
	@docker build -t gardenlinux/integration-test:$(VERSION) integration-test

.PHONY: clean
clean:
	-@[ -n "$$(docker image ls gardenlinux/integration-test --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/integration-test --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(docker image ls gardenlinux/build-image --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/build-image --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(docker image ls gardenlinux/build-deb --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/build-deb --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(docker image ls gardenlinux/build --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/build --format "{{.Repository}}:{{.Tag}}"); true
	-@[ -n "$$(docker image ls gardenlinux/slim --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/slim --format "{{.Repository}}:{{.Tag}}"); true
