FROM gcr.io/kaniko-project/executor:latest as kaniko


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
ENV PATH=${PATH}:/opt/debuerreotype/bin
COPY	--from=kaniko /kaniko/executor /kaniko/executor
COPY hack/debootstrap.patch /tmp/debootstrap.patch
RUN	patch -p1 < /tmp/debootstrap.patch \
     && echo "progress=bar:force:noscroll" >> /etc/wgetrc \
     && rm /tmp/debootstrap.patch

WORKDIR /tmp
