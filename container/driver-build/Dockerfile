FROM ghcr.io/gardenlinux/gardenlinux:nightly

ENV DEBIAN_FRONTEND noninteractive
ENV SHELL /bin/bash

RUN apt-get update && \
    apt-get install -y  \
        sudo vim git rsync wget curl gnupg python3 build-essential bc kmod cpio \
        flex libelf-dev libssl-dev dwarves \
        devscripts kernel-wedge pristine-lfs python3-debian quilt dkms

RUN sudo dpkg --add-architecture arm64
RUN sudo dpkg --add-architecture amd64

# Install Garden Linux kernel header meta packages 
# Note: https://gitlab.com/gardenlinux/gardenlinux-package-linux
RUN apt-get update && \
    apt-get install -y \
        kmod \
        linux-headers-cloud-amd64 \
        linux-headers-cloud-arm64 \
        linux-headers-amd64 \
        linux-headers-arm64
