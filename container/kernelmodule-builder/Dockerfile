FROM debian:bookworm-slim

ARG GLSUITE
ARG KERNEL_VERSION
ARG GNU_TYPE_PACKAGE
ARG TARGET_ARCH

RUN dpkg --add-architecture $TARGET_ARCH
RUN apt-get update -qy

# Include software for compiling and debugging kernel module source code
RUN apt-get install -qy sudo vim git rsync wget curl gnupg python3 build-essential bc kmod cpio \
			flex libncurses5-dev libelf-dev libssl-dev dwarves \
            		devscripts kernel-wedge pristine-lfs python3-debian quilt dkms

# Include architecture dependend software required to compile kernel modules
RUN apt-get install -qy --no-install-recommends \ 
        binutils-$GNU_TYPE_PACKAGE gcc-$GNU_TYPE_PACKAGE \
        g++-$GNU_TYPE_PACKAGE libc6-dev:$TARGET_ARCH

# Many kernelmodule build setups take the output of "uname -r" to find the kernel headers. 
# The following lines add a uname wrapper to tell these kernelmodule builds to use the garden linux headers
RUN mv /bin/uname /bin/uname-orig
ADD ./bin/* /bin/

ADD gardenlinux.asc /etc/apt/trusted.gpg.d/gardenlinux.asc

# Setup Garden Linux apt repository
RUN echo -n "deb https://repo.gardenlinux.io/gardenlinux ${GLSUITE} main" >> /etc/apt/sources.list

RUN cat /etc/apt/sources.list

# Install kernel headers for all supported flavors
RUN apt-get update -qy
RUN apt-get install -qy "linux-headers-${KERNEL_VERSION}-gardenlinux-${TARGET_ARCH}" \
			"linux-headers-${KERNEL_VERSION}-gardenlinux-cloud-${TARGET_ARCH}" \
			"linux-headers-${KERNEL_VERSION}-gardenlinux-firecracker-${TARGET_ARCH}"
