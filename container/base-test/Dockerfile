ARG DEBIAN_DIST=stable
FROM debian:${DEBIAN_DIST}-slim
ARG DEBIAN_DIST

ENV DEBIAN_FRONTEND noninteractive
ENV SHELL /bin/bash
ENV PYTHONPATH /gardenlinux/bin:/gardenlinux/ci:/gardenlinux/ci/glci:/gardenlinux/tests:/gardenlinux/features

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates

RUN echo "deb http://deb.debian.org/debian ${DEBIAN_DIST} main contrib non-free" > /etc/apt/sources.list \
     && sed -i 's/deb.debian.org/cdn-aws.deb.debian.org/g' /etc/apt/sources.list \
     && if [ -f "/etc/apt/sources.list.d/debian.sources" ] ; then sed -i 's/deb.debian.org/cdn-aws.deb.debian.org/g' /etc/apt/sources.list.d/debian.sources ; else echo "file not present" ; fi \
     && apt-get update \
     && apt-get install -y --no-install-recommends \
          curl \
          unzip \
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
          libpython3-dev

# Prepare virtual environment
# We need a virtual env to install packages via pip, and not via apt.
# See: https://peps.python.org/pep-0668/
ENV VIRTUAL_ENV_PARENT=/opt/python-test-env
ENV VIRTUAL_ENV="$VIRTUAL_ENV_PARENT/.venv"
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY Pipfile Pipfile.lock "$VIRTUAL_ENV_PARENT/"
# Do not use --system, we want the pip from the virtual env
RUN cd "$VIRTUAL_ENV_PARENT" && pipenv install --dev 
WORKDIR /gardenlinux/tests
