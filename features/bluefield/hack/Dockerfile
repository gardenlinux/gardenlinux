FROM ghcr.io/gardenlinux/gardenlinux:nightly

RUN  mkdir /etc/sudoers.d && \
     echo "%wheel ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/wheel && \
     echo "debconf debconf/frontend select Noninteractive" | debconf-set-selections && \
     echo "APT::Install-Recommends false;\nAPT::Install-Suggests false;\nApt::AutoRemove::SuggestsImportant false;\n" > /etc/apt/apt.conf.d/no-recommends && \
     echo "progress=bar:force:noscroll" >> /etc/wgetrc && \
     echo "force-confold\nforce-confdef" > /etc/dpkg/dpkg.cfg.d/forceold 

RUN  echo "deb http://deb.debian.org/debian testing main" > /etc/apt/sources.list.d/testing.list
RUN  echo "deb https://packages.gardenlinux.io/gardenlinux today main" > /etc/apt/sources.list
RUN  apt-get update && \
     apt-get install -y --no-install-recommends ca-certificates sudo wget devscripts fakeroot && \
     groupadd --system wheel && \
     useradd dev -s /bin/bash -d /home/dev -m -G wheel

RUN apt install -y -f --allow-downgrades \
        linux-image-6.6.43-arm64=6.6.43-0gardenlinux0 \
        linux-headers-6.6.43-arm64=6.6.43-0gardenlinux0 \
        linux-source-6.6

USER dev
WORKDIR	/home/dev
