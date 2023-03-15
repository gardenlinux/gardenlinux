# TODO: switch to gardenlinux-slim
FROM debian:bookworm-slim
ARG	GARDENLINUX_MIRROR_KEY=/etc/apt/trusted.gpg.d/gardenlinux.asc
ARG VERSION
ARG GNU_TYPE_PACKAGE
ARG ARCH


RUN dpkg --add-architecture "$ARCH"

# Setup Garden Linux Repository
COPY gardenlinux.asc $GARDENLINUX_MIRROR_KEY
RUN  chown root:root $GARDENLINUX_MIRROR_KEY \
        && chmod 644 $GARDENLINUX_MIRROR_KEY

# ca-certificates is required to verify repo.gardenlinux.io
RUN apt-get update && apt-get install -qy --no-install-recommends ca-certificates

# Pin linux-* packages to the garden linux repo, while keeping build dependency tools in debian mirror repo
ADD ./gardenlinux-apt-preferences /etc/apt/preferences.d/gardenlinux

RUN echo "deb [signed-by=$GARDENLINUX_MIRROR_KEY] https://repo.gardenlinux.io/gardenlinux $VERSION main" >> /etc/apt/sources.list.d/gardenlinux-$VERSION.list 

# Install garden linux kernel header and debug definitions
RUN apt-get update && \
    apt-get install -qy --no-install-recommends \
    linux-headers-6.1-${ARCH} \
    linux-image-6.1-${ARCH}-dbg \
    linux-kbuild-6.1
    
# Install general kernel module build dependencies
RUN apt-get update && \
    apt-get install -qy --no-install-recommends \
    bc \
    build-essential \
    cpio \
    curl \
    devscripts \
    dkms \
    dwarves \
    flex \
    git \
    gnupg \
    kernel-wedge \
    kmod \
    kpatch \
    kpatch-build \
    libelf-dev \
    libncurses5-dev \
    libssl-dev \
    pristine-lfs \
    python3 \
    python3-debian \
    quilt \
    rsync \
    sudo \
    vim \
    wget    
