FROM golang:latest as golang
RUN go get -u golang.org/x/lint/golint \
     && git clone https://github.com/microsoft/azure-vhd-utils.git \
     && cd azure-vhd-utils \
     && make


FROM gardenlinux/slim

ENV DEBIAN_FRONTEND noninteractive
ENV SHELL /bin/bash
ENV PYTHONPATH /gardenlinux/bin:/gardenlinux/ci:/gardenlinux/ci/glci

RUN apt-get update \
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
     && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
     && unzip awscliv2.zip \
     && ./aws/install \
     && rm -rf ./aws \
     && curl -sL -o /usr/share/keyrings/cloud.google.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg \
     && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
     && apt-get update \
     && apt-get install -y google-cloud-sdk \
     && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg \
     && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ bullseye main" | tee /etc/apt/sources.list.d/azure-cli.list \
     && apt-get update \
     && apt-get install -y azure-cli \
     && pip3 install python-openstackclient \
     && curl -sL -o /aliyun-cli-linux-3.0.94-amd64.tgz https://github.com/aliyun/aliyun-cli/releases/download/v3.0.94/aliyun-cli-linux-3.0.94-amd64.tgz \
     && (cd /usr/local/bin ; tar xf /aliyun-cli-linux-3.0.94-amd64.tgz) \
     && rm /aliyun-cli-linux-3.0.94-amd64.tgz \
     && curl -sL -o /usr/local/bin/ossutil https://gosspublic.alicdn.com/ossutil/1.7.6/ossutil64?spm=a2c63.p38356.a3.3.44692454KkczI0  \
     && chmod 755 /usr/local/bin/ossutil \
     && apt-get clean && rm -rf /var/lib/apt/lists/* \
     && mkdir -p /root/.aws /root/.ssh /config \
     && (test -x /usr/bin/pytest-3 && ln -sf /usr/bin/pytest-3 /usr/bin/pytest)

COPY _pipfiles /_pipfiles
RUN cd /_pipfiles && pipenv --python 3.9 install --system --dev && cd / && rm -rf /_pipfiles

COPY --from=golang /go/azure-vhd-utils/azure-vhd-utils /usr/local/bin/azure-vhd-utils

WORKDIR /gardenlinux/tests
