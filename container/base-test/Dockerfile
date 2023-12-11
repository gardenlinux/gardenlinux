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
     && echo "deb [signed-by=$GARDENLINUX_MIRROR_KEY] https://repo.gardenlinux.io/gardenlinux $VERSION main" >> /etc/apt/sources.list \
     && sed -i 's/deb.debian.org/cdn-aws.deb.debian.org/g' /etc/apt/sources.list \
     && if [ -f "/etc/apt/sources.list.d/debian.sources"] ; then sed -i 's/deb.debian.org/cdn-aws.deb.debian.org/g' /etc/apt/sources.list.d/debian.sources ; else echo "file not present" ; fi \
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
          python3-venv \
          pipenv \
          vim \
          procps \
          openssh-client \
          inetutils-ping \
          wget \
          iproute2 \
          guestfish \
          qemu-system-x86 \
          qemu-system-arm \
          qemu-efi-aarch64 \
          shellcheck \
          build-essential \
          libpython3-dev \
          onmetal-image

# Prepare virtual environment
# We need a virtual env to install packages via pip, and not via apt.
# See: https://peps.python.org/pep-0668/
ENV VIRTUAL_ENV_PARENT=/opt/python-test-env
ENV VIRTUAL_ENV="$VIRTUAL_ENV_PARENT/.venv"
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY Pipfile* "$VIRTUAL_ENV_PARENT/"
# Do not use --system, we want the pip from the virtual env
RUN cd "$VIRTUAL_ENV_PARENT" && pipenv install --dev 
WORKDIR /gardenlinux/tests
