# use latest nightly by default
ARG GL_VERSION=nightly
ARG GL_BASE=ghcr.io/gardenlinux/gardenlinux:${GL_VERSION}

FROM ${GL_BASE}

ENV PYTHON=python3.13

ENV DEBIAN_FRONTEND noninteractive
ENV SHELL /bin/bash
ENV PYTHONPATH /gardenlinux/bin:/gardenlinux/ci:/gardenlinux/ci/glci:/gardenlinux/tests:/gardenlinux/features

# install some basic tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       curl \
       unzip \
       less \
       apt-transport-https \
       gnupg \
       gpgv \
       # python from GL repos, all python packages are supposed to come from pip
       ${PYTHON}-venv \
       lib${PYTHON}-dev \
       vim \
       procps \
       openssh-client \
       inetutils-ping \
       wget \
       iproute2 \
       jq \
       guestfish \
       # qemu-img is used in some scripts
       qemu-utils \
       qemu-system-x86 \
       qemu-system-arm \
       qemu-efi-aarch64 \
       shellcheck \
       build-essential \
       onmetal-image \
       psmisc \
       git \
       #### needed to install libvirt-python via pipenv
       pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Prepare virtual environment
# We need a virtual env to install packages via pip, and not via apt.
# See: https://peps.python.org/pep-0668/
ENV VIRTUAL_ENV_PARENT=/opt/python-test-env
ENV VIRTUAL_ENV="$VIRTUAL_ENV_PARENT/.venv"
RUN ${PYTHON} -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY Pipfile Pipfile.lock "$VIRTUAL_ENV_PARENT/"
# Do not use --system, we want the pip from the virtual env
RUN cd "$VIRTUAL_ENV_PARENT" && pip install pipenv && pipenv install --categories "packages dev-packages"
WORKDIR /gardenlinux/tests
