FROM	debian:stable-slim

ENV     DEBIAN_FRONTEND noninteractive

RUN	apt-get update \
     &&	apt-get install debian-archive-keyring \
     &&	echo "deb http://archive.debian.org/debian/ sarge main [trusted=yes]" >> /etc/apt/sources.list.d/damnold.list \
     &&	apt-get update \
     &&	apt-get install git ruby libdbd-pg-ruby1.8 libbz2-ruby1.8 libbz2-ruby1.8 python-yaml python-psycopg2 python-lockfile fuse-utils python-fuse uuid-runtime \
     &&	git clone https://salsa.debian.org/snapshot-team/snapshot.git

