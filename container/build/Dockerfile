ARG  build_base_image=gardenlinux/slim
FROM	$build_base_image

ARG	DEBIAN_FRONTEND=noninteractive
COPY	checksums.sha256 /checksums.sha256

RUN	mkdir /etc/sudoers.d \
     &&	echo "%wheel ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/wheel \
     && echo "deb-src https://deb.debian.org/debian testing main" >> /etc/apt/sources.list \
     &&	echo "#deb https://deb.debian.org/debian unstable main" >> /etc/apt/sources.list \
     && echo "#deb-src https://deb.debian.org/debian unstable main" >> /etc/apt/sources.list \
     && sed -i 's/deb.debian.org/cdn-aws.deb.debian.org/g' /etc/apt/sources.list \
     && echo "APT::Install-Recommends false;\nAPT::Install-Suggests false;\nApt::AutoRemove::SuggestsImportant false;\n" > /etc/apt/apt.conf.d/no-recommends \
     &&	echo "progress=bar:force:noscroll" >> /etc/wgetrc \
     &&	echo "force-confold\nforce-confdef" > /etc/dpkg/dpkg.cfg.d/forceold

ARG	BUILDARCH=amd64

ADD	https://cdn-aws.deb.debian.org/debian/pool/main/g/gcc-defaults/gcc_10.2.1-1_${BUILDARCH}.deb /
ADD	https://cdn-aws.deb.debian.org/debian/pool/main/g/gcc-defaults/g++_10.2.1-1_${BUILDARCH}.deb /
ADD	https://cdn-aws.deb.debian.org/debian/pool/main/g/gcc-defaults/cpp_10.2.1-1_${BUILDARCH}.deb /

RUN	apt-get update \
     && apt-get install -y wget ca-certificates coreutils \
     && sha256sum -c --ignore-missing /checksums.sha256 \
     &&	if [ "${BUILDARCH}" = "amd64" ] ; then wget https://cdn-aws.deb.debian.org/debian/pool/main/g/gcc-defaults/gcc-multilib_10.2.1-1_${BUILDARCH}.deb; fi \
     &&	apt-get install -y -f /*.deb \
     &&	apt-mark auto gcc g++ cpp gcc-multilib \
     &&	rm -f /*.deb \
     &&	dpkg -P gcc-9-base \
     &&	apt-get install -y build-essential fakeroot sudo gettext uuid-runtime efitools \
     &&	addgroup --system wheel \
     &&	adduser dev --disabled-password --gecos dev \
     &&	adduser dev wheel

COPY install-cfssl.sh /setup/
RUN  /setup/install-cfssl.sh

USER	dev
WORKDIR	/home/dev

RUN 	mkdir .gnupg && chmod 700 .gnupg
