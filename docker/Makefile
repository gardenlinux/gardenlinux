VERSION=`../bin/garden-version`

all: build-image

.PHONY: needslim
needslim:
	./needslim

.PHONY: build-image
build-image: needslim 
	@docker build -t gardenlinux/build-image:$(VERSION) build-image

.PHONY: build
build: needslim
	@docker build -t gardenlinux/build build

.PHONY: build-deb
build-deb: build
	@docker build -t gardenlinux/build-deb build-deb
