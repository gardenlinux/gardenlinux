ARG VERSION
FROM gardenlinux/base-test:${VERSION}
ENV SHELL /bin/bash

RUN : "Install AWS requirements" \
     && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
     && unzip awscliv2.zip \
     && ./aws/install \
     && rm -rf ./aws && \
    : "Install GCP requirements" \
     && curl -sL -o /usr/share/keyrings/cloud.google.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg \
     && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
     && apt-get update \
     && apt-get install -y google-cloud-sdk && \
    : "Azure and OpenStack cli already installed in gardenlinux/base-test image" \
    : "Install AliCloud specific requirements" \
     && curl -sL -o /aliyun-cli-linux-3.0.94-amd64.tgz https://github.com/aliyun/aliyun-cli/releases/download/v3.0.94/aliyun-cli-linux-3.0.94-amd64.tgz \
     && (cd /usr/local/bin ; tar xf /aliyun-cli-linux-3.0.94-amd64.tgz) \
     && rm /aliyun-cli-linux-3.0.94-amd64.tgz \
     && curl -sL -o /usr/local/bin/ossutil https://gosspublic.alicdn.com/ossutil/1.7.6/ossutil64?spm=a2c63.p38356.a3.3.44692454KkczI0  \
     && chmod 755 /usr/local/bin/ossutil \
     && apt-get clean && rm -rf /var/lib/apt/lists/* \
     && mkdir -p /root/.aws /root/.ssh /config && \
   : "Install firecracker specific binaries" \
     && firecracker_ver="v1.1.1" \
     && release_url="https://github.com/firecracker-microvm/firecracker/releases" \
     && echo ${release_url}/download/${firecracker_ver}/firecracker-${firecracker_ver}-${arch}.tgz \
     && curl -L ${release_url}/download/${firecracker_ver}/firecracker-${firecracker_ver}-${arch}.tgz | tar -xz \
     && ln -s /release-${firecracker_ver}-${arch}/firecracker-${firecracker_ver}-${arch} /bin/firecracker

WORKDIR /gardenlinux/tests
