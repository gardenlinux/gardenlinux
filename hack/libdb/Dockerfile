FROM	debian:testing-slim

RUN     echo "deb-src http://deb.debian.org/debian testing main" >> /etc/apt/sources.list \
     &&	apt-get update \
     &&	apt-get install -y --no-install-recommends build-essential fakeroot sudo \
     && addgroup --system wheel \
     && adduser dev --disabled-password --gecos dev \
     && adduser dev wheel \
     && echo "%wheel  ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/wheel

USER	dev
WORKDIR	/home/dev
