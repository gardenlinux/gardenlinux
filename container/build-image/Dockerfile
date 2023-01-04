ARG	build_base_image=gardenlinux/slim
FROM	$build_base_image
ARG	DEBIAN_FRONTEND=noninteractive
ARG	GARDENLINUX_MIRROR_KEY=/etc/apt/trusted.gpg.d/gardenlinux.asc
ARG	VERSION

COPY gardenlinux.asc $GARDENLINUX_MIRROR_KEY
RUN  chown root:root $GARDENLINUX_MIRROR_KEY \
        && chmod 644 $GARDENLINUX_MIRROR_KEY

RUN if [ "$(dpkg --print-architecture)" != amd64 ]; then dpkg --add-architecture amd64; fi

RUN : "Initialize the build container package installation" \
		&& sed -i 's/deb.debian.org/cdn-aws.deb.debian.org/g' /etc/apt/sources.list \
		&& arch="$(dpkg --print-architecture)" \
		&& apt-get update \
		&& apt-get install -y --no-install-recommends \
			wget \
			ca-certificates \
		&& \
	: "Extend the sources with other required repos" \
		&& echo "deb [signed-by=$GARDENLINUX_MIRROR_KEY] https://repo.gardenlinux.io/gardenlinux $VERSION main" >> /etc/apt/sources.list \
		&& echo "deb https://cdn-aws.deb.debian.org/debian unstable main" >> /etc/apt/sources.list \
		&& echo 'APT::Default-Release "testing";' > /etc/apt/apt.conf.d/default-testing \
		&& apt-get update \
		&& \
	: "Install all required build tools" \
		&& apt-get install -y --no-install-recommends \
			debian-ports-archive-keyring \
			debootstrap \
			gettext-base \
			dosfstools mtools datefudge squashfs-tools e2fsprogs \
			fdisk mount cryptsetup gnupg xz-utils bsdextrautils \
			sbsigntool \
			libcap2-bin \
			python3 \
			python3-mako \
			python3-yaml \
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
			qemu-system-x86 \
			openssl \
			podman fuse-overlayfs \
			libengine-pkcs11-openssl \
			onmetal-image \
			oras \
			libaws-sdk-cpp-dev \
			aws-kms-pkcs11 \
			systemd \
		&& apt-get install -t unstable -y --no-install-recommends \
			binutils-x86-64-linux-gnu \
			binutils-aarch64-linux-gnu \
		&& \
	: "Clean up repo files" \
		&& rm -rf /var/lib/apt/lists/*

ENV	PATH=${PATH}:/opt/gardenlinux/bin
RUN	echo "progress=bar:force:noscroll\nverbose=off" >> /etc/wgetrc
WORKDIR	/tmp
