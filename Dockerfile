FROM 	gcr.io/kaniko-project/executor:latest as kaniko

FROM	golang:latest as azure
RUN	go get -u golang.org/x/lint/golint \
     && git clone https://github.com/microsoft/azure-vhd-utils.git \
     && cd azure-vhd-utils \
     && make

FROM 	debian:testing-slim
RUN	apt-get update \
     && apt-get install -y --no-install-recommends \
		debian-ports-archive-keyring \
		debootstrap patch \
		wget ca-certificates \
		\
		gnupg dirmngr \
		qemu-user-static \
		dosfstools squashfs-tools e2fsprogs \
		fdisk mount \
		xz-utils \
		qemu-utils \
		python3 \
		python3-mako \
     && rm -rf /var/lib/apt/lists/*

# repo-root requires to be mounted at /debuerreotype
ENV 	PATH=${PATH}:/opt/debuerreotype/bin
COPY	--from=kaniko /kaniko/executor /usr/local/bin/executor
COPY	--from=azure  /go/azure-vhd-utils/azure-vhd-utils /usr/local/bin/azure-vhd-utils
COPY 	hack/debootstrap.patch /tmp/debootstrap.patch
RUN	patch -p1 < /tmp/debootstrap.patch \
     && rm /tmp/debootstrap.patch \
     && echo "progress=bar:force:noscroll" >> /etc/wgetrc

WORKDIR	/tmp
