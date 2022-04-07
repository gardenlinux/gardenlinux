ARG build_base_image=gardenlinux/slim
FROM	golang:latest as golang
COPY	garden-feat.go /go/src
RUN	go install golang.org/x/lint/golint@latest \
     && cd /go/src \
     && golint garden-feat.go \
     && go mod init garden-feat.go \
     && go mod tidy -go=1.16 \
     && go mod tidy -go=1.17 \
     && go build garden-feat.go

FROM 	$build_base_image
ARG	DEBIAN_FRONTEND=noninteractive

RUN if [ "$(dpkg --print-architecture)" != amd64 ]; then dpkg --add-architecture amd64; fi

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		debian-ports-archive-keyring \
		debootstrap \
		wget ca-certificates gettext-base \
		dosfstools mtools datefudge squashfs-tools e2fsprogs \
		fdisk mount cryptsetup gnupg xz-utils bsdextrautils \
		sbsigntool \
		libcap2-bin \
		python3 \
		python3-mako \
		qemu-user-static \
		qemu-utils \
		cpio \
		syslinux:amd64 syslinux-common:amd64 isolinux:amd64 xorriso:amd64 \
		dpkg-dev \
		procps \
		iproute2 \
		rsync \
		openssh-client \
		qemu-system-arm \
		qemu-system-x86


RUN echo "deb https://deb.debian.org/debian unstable main" >> /etc/apt/sources.list \
	&& echo 'APT::Default-Release "testing";' > /etc/apt/apt.conf.d/default-testing \
	&& apt-get update \
	&& apt-get install -t unstable -y --no-install-recommends binutils-x86-64-linux-gnu binutils-aarch64-linux-gnu

RUN rm -rf /var/lib/apt/lists/*

ENV	PATH=${PATH}:/opt/gardenlinux/bin
#COPY	--from=gcr.io/kaniko-project/executor:latest /kaniko/executor /usr/local/bin/executor
COPY	--from=golang /go/src/garden-feat /usr/local/bin/garden-feat
RUN	echo "progress=bar:force:noscroll\nverbose=off" >> /etc/wgetrc

WORKDIR	/tmp
