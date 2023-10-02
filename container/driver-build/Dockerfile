FROM ghcr.io/gardenlinux/gardenlinux:nightly

ENV DEBIAN_FRONTEND noninteractive
ENV SHELL /bin/bash

RUN apt-get update && \
    apt-get install -y  \
        sudo vim git rsync wget curl gnupg python3 build-essential bc kmod cpio \
        flex libelf-dev libssl-dev dwarves \
        devscripts kernel-wedge pristine-lfs python3-debian quilt dkms

# Install Garden Linux Kernel meta packages 
# Note: https://gitlab.com/gardenlinux/gardenlinux-package-linux
RUN ARCH=$(dpkg --print-architecture) && \
    apt-get update && \
    apt-get install -y \
        kmod \
        linux-headers-cloud-${ARCH} \
        linux-headers-${ARCH}