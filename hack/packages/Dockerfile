FROM	debian:testing-slim

RUN     echo "deb-src http://deb.debian.org/debian testing main" >> /etc/apt/sources.list \
     && echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections \
     &&	apt-get update \
     && bash -xc " \
        apt-get install -y --no-install-recommends wget apt-utils; \
        wget -P / http://deb.debian.org/debian/pool/main/g/gcc-defaults/{gcc,g++,cpp,gcc-multilib}_10-1_amd64.deb; \
        apt-get install -y --no-install-recommends -f /{gcc,g++,cpp,gcc-multilib}_10-1_amd64.deb; \
        apt-mark auto gcc g++ cpp gcc-multilib; \
        rm /{gcc,g++,cpp,gcc-multilib}_10-1_amd64.deb" \
     && dpkg -P gcc-9-base \
     &&	apt-get install -y --no-install-recommends build-essential fakeroot sudo devscripts \
     && addgroup --system wheel \
     && adduser dev --disabled-password --gecos dev \
     && adduser dev wheel \
     && echo "%wheel  ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/wheel \
     && mkdir /home/dev/.gnupg \
     && chown dev:dev /home/dev/.gnupg \
     && chmod 700 /home/dev/.gnupg 

USER	dev
WORKDIR	/home/dev
