FROM golang:latest as golang
RUN go get -u golang.org/x/lint/golint \
     && git clone https://github.com/microsoft/azure-vhd-utils.git \
     && cd azure-vhd-utils \
     && make

FROM gardenlinux/slim

ENV DEBIAN_FRONTEND noninteractive
ENV SHELL /bin/bash
ENV PYTHONPATH=/gardenlinux/bin:/gardenlinux/ci

RUN	apt-get update \
     &&	apt-get install -y --no-install-recommends \
		curl \
		unzip \
        ca-certificates \
        less \
        apt-transport-https gnupg \
        pipenv \
        vim-tiny \
        procps \
        openssh-client \
        inetutils-ping \
     && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
     && unzip awscliv2.zip \
     && ./aws/install \
     && rm -rf ./aws \
	 && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
     && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
     && apt-get update \
     && apt-get install -y google-cloud-sdk \
     && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null \
     && echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ bullseye main" | tee /etc/apt/sources.list.d/azure-cli.list \
     && apt-get update \
     && apt-get install -y azure-cli \
     &&	rm -rf /var/lib/apt/lists/*

copy --from=golang /go/azure-vhd-utils/azure-vhd-utils /usr/local/bin/azure-vhd-utils

WORKDIR	/gardenlinux/tests
