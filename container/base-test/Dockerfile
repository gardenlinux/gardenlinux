FROM gardenlinux/slim

ENV DEBIAN_FRONTEND noninteractive
ENV SHELL /bin/bash
ENV PYTHONPATH /gardenlinux/bin:/gardenlinux/ci:/gardenlinux/ci/glci:/gardenlinux/tests:/gardenlinux/features
ARG GARDENLINUX_MIRROR_KEY=/etc/apt/trusted.gpg.d/gardenlinux.asc
ARG VERSION

COPY gardenlinux.asc $GARDENLINUX_MIRROR_KEY
RUN  chown root:root $GARDENLINUX_MIRROR_KEY \
        && chmod 644 $GARDENLINUX_MIRROR_KEY

RUN echo "deb http://deb.debian.org/debian testing main contrib non-free" > /etc/apt/sources.list \
     && echo "deb [signed-by=$GARDENLINUX_MIRROR_KEY] http://repo.gardenlinux.io/gardenlinux $VERSION main" >> /etc/apt/sources.list \
     && sed -i 's/deb.debian.org/cdn-aws.deb.debian.org/g' /etc/apt/sources.list \
     && apt-get update \
     && apt-get install -y --no-install-recommends \
          curl \
          unzip \
          ca-certificates \
          less \
          apt-transport-https \
          gnupg \
          python3-pip \
          python3-pytest \
          vim \
          procps \
          openssh-client \
          inetutils-ping \
          wget \
          iproute2 \
          libguestfs-tools \
          qemu-system-x86 \
          qemu-system-arm \
          qemu-efi-aarch64 \
          shellcheck \
          build-essential \
          libpython3-dev \
          onmetal-image

# pipenv package was removed from bookworm https://tracker.debian.org/pkg/pipenv
RUN pip install pipenv==2022.4.8
COPY _pipfiles /_pipfiles
RUN cd /_pipfiles && pipenv --python 3.10 install --system --skip-lock --dev && cd / && rm -rf /_pipfiles

WORKDIR /gardenlinux/tests
