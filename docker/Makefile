VERSION=`../bin/garden-version`

all: build-image

.PHONY: needslim
needslim:
	@./needslim

.PHONY: build-image
build-image: needslim 
	@docker build -t gardenlinux/build-image:$(VERSION) build-image

.PHONY: build
build: needslim
	@docker build -t gardenlinux/build build

.PHONY: build-deb
build-deb: build
	@docker build -t gardenlinux/build-deb build-deb

.PHONY: clean
clean:
	-@[ -n "$$(docker image ls gardenlinux/build-image --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/build-image --format "{{.ID}}"); true
	-@[ -n "$$(docker image ls gardenlinux/build-deb --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/build-deb --format "{{.ID}}")i; true
	-@[ -n "$$(docker image ls gardenlinux/build --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/build --format "{{.ID}}"); true
	-@[ -n "$$(docker image ls gardenlinux/slim --format "{{.ID}}")" ] && docker image rm --force $$(docker image ls gardenlinux/slim --format "{{.ID}}"); true
