FROM	debian:testing-slim

ENV     DEBIAN_FRONTEND noninteractive

RUN	apt-get update \
     &&	apt-get install -y reprepro gpg libgpgme11 \
     &&	gpg --list-keys \
     &&	rm -rf /var/lib/apt/lists
