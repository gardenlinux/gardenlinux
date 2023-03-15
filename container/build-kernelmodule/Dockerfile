# TODO: switch to gardenlinux-slim
FROM debian:bookworm-slim
ARG	GARDENLINUX_MIRROR_KEY=/etc/apt/trusted.gpg.d/gardenlinux.asc
ARG VERSION

# Setup Garden Linux Repository
COPY gardenlinux.asc $GARDENLINUX_MIRROR_KEY
RUN  chown root:root $GARDENLINUX_MIRROR_KEY \
        && chmod 644 $GARDENLINUX_MIRROR_KEY

# ca-certificates is required to verify repo.gardenlinux.io
RUN apt-get update && apt-get install -qy --no-install-recommends ca-certificates
ADD ./gardenlinux-apt-preferences /etc/apt/preferences.d/gardenlinux

RUN echo "deb [signed-by=$GARDENLINUX_MIRROR_KEY] https://repo.gardenlinux.io/gardenlinux $VERSION main" >> /etc/apt/sources.list.d/gardenlinux-$VERSION.list 



# Install kernel live patch builder dependency
RUN apt-get update && \
    apt-get install -qy --no-install-recommends \
    linux-image-6.1-amd64-dbg \
    linux-headers-6.1-amd64 \
    linux-kbuild-6.1 \
    kpatch \
    kpatch-build
    
