ARG build_base_image=gardenlinux/slim
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
		libengine-pkcs11-openssl

RUN arch="$(dpkg --print-architecture)" && \
	wget "https://gardenlinux-aws-kms-pkcs11.s3.eu-central-1.amazonaws.com/aws-sdk-cpp_$arch.deb" "https://gardenlinux-aws-kms-pkcs11.s3.eu-central-1.amazonaws.com/aws-kms-pkcs11_$arch.deb" && \
	apt-get install -y --no-install-recommends "./aws-sdk-cpp_$arch.deb" "./aws-kms-pkcs11_$arch.deb"

RUN echo "deb https://deb.debian.org/debian unstable main" >> /etc/apt/sources.list \
	&& echo 'APT::Default-Release "testing";' > /etc/apt/apt.conf.d/default-testing \
	&& apt-get update \
	&& apt-get install -t unstable -y --no-install-recommends binutils-x86-64-linux-gnu binutils-aarch64-linux-gnu

RUN rm -rf /var/lib/apt/lists/*

ENV	PATH=${PATH}:/opt/gardenlinux/bin
RUN	echo "progress=bar:force:noscroll\nverbose=off" >> /etc/wgetrc
WORKDIR	/tmp
