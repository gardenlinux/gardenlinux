ARG build_base_image=gardenlinux/slim
FROM	golang:latest as golang
RUN	go get -u golang.org/x/lint/golint \
     &&	git clone https://github.com/microsoft/azure-vhd-utils.git \
     &&	cd azure-vhd-utils \
     &&	make

FROM 	$build_base_image
ARG	DEBIAN_FRONTEND=noninteractive

RUN	apt-get update \
     &&	apt-get install -y --no-install-recommends \
		debian-ports-archive-keyring \
		debootstrap patch \
		wget ca-certificates gettext-base \
		dosfstools squashfs-tools e2fsprogs \
		fdisk mount gnupg xz-utils bsdextrautils \
		\
		libcap2-bin \
		python3 \
		python3-mako \
		qemu-user-static \
		qemu-utils \
		cpio \
     &&	rm -rf /var/lib/apt/lists/*

ENV	PATH=${PATH}:/opt/gardenlinux/bin
COPY	--from=gcr.io/kaniko-project/executor:latest /kaniko/executor /usr/local/bin/executor
COPY	--from=golang /go/azure-vhd-utils/azure-vhd-utils /usr/local/bin/azure-vhd-utils
COPY	debootstrap.patch /tmp/debootstrap.patch
RUN	patch -p1 < /tmp/debootstrap.patch \
     &&	rm -f /tmp/debootstrap.patch \
     &&	echo "progress=bar:force:noscroll\nverbose=off" >> /etc/wgetrc

WORKDIR	/tmp
