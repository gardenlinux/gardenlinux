FROM gardenlinux/slim

ENV DEBIAN_FRONTEND noninteractive
ENV SHELL /bin/bash
ENV PYTHONPATH /gardenlinux/bin:/gardenlinux/ci:/gardenlinux/ci/glci:/gardenlinux/tests:/gardenlinux/features

RUN echo "deb http://deb.debian.org/debian testing main contrib non-free" > /etc/apt/sources.list \
     && apt-get update \
     && apt-get install -y --no-install-recommends \
          curl \
          unzip \
          ca-certificates \
          less \
          apt-transport-https \
          gnupg \
          pipenv \
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
          shellcheck \
          build-essential \
          libpython3-dev \
     && (test -x /usr/bin/pytest-3 && ln -sf /usr/bin/pytest-3 /usr/bin/pytest)

COPY _pipfiles /_pipfiles
RUN cd /_pipfiles && pipenv --python 3.9 install --system --dev && cd / && rm -rf /_pipfiles

WORKDIR /gardenlinux/tests
