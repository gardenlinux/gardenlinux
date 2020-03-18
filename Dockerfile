# docker run --cap-add SYS_ADMIN --cap-drop SETFCAP --tmpfs /tmp:dev,exec,suid,noatime ...

# bootstrapping a new architecture?
#   ./scripts/debuerreotype-init /tmp/docker-rootfs buster now
#   ./scripts/debuerreotype-minimizing-config /tmp/docker-rootfs
#   ./scripts/debuerreotype-debian-sources-list /tmp/docker-rootfs buster
#   ./scripts/debuerreotype-tar /tmp/docker-rootfs - | docker import - debian:buster-slim
# alternate:
#   debootstrap --variant=minbase buster /tmp/docker-rootfs
#   tar -cC /tmp/docker-rootfs . | docker import - debian:buster-slim
# (or your own favorite set of "debootstrap" commands to create a base image for building this one FROM)
FROM debian:testing-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
		debian-ports-archive-keyring \
		debootstrap \
		wget ca-certificates \
		xz-utils \
		curl \
		\
		gnupg dirmngr 
		parted udev dosfstools xz-utils \
	&& rm -rf /var/lib/apt/lists/*

# see ".dockerignore"
COPY . /opt/debuerreotype
RUN set -ex; \
	cd /opt/debuerreotype/scripts; \
	for f in debuerreotype-*; do \
		ln -svL "$PWD/$f" "/usr/local/bin/$f"; \
	done; \
	version="$(debuerreotype-version)"; \
	[ "$version" != 'unknown' ]; \
	echo "debuerreotype version $version"

WORKDIR /tmp

