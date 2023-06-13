ARG VERSION
FROM gardenlinux/base-test:${VERSION}
ENV SHELL /bin/bash
COPY checksums.sha256 /gardenlinux/tests/checksums.sha256
COPY cloud.google.gpg /usr/share/keyrings/cloud.google.gpg

#Virtual Env Created in base-test
ENV VIRTUAL_ENV="/opt/python-test-env/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN : "Install AWS requirements" \
     && pip install awscliv2 \
     && awsv2 --install
RUN : "Install GCP requirements" \
     && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
     && apt-get update \
     && apt-get install -y google-cloud-sdk
RUN : "Azure and OpenStack cli already installed in gardenlinux/base-test image" \
    : "Install AliCloud specific requirements" \
     && arch="$(uname -m)" \
     && [ $arch = "x86_64" ] && aliyun_arch=amd64 || aliyun_arch=arm64 \
     && [ $arch = "x86_64" ] && ossutil_arch=64 || ossutil_arch=arm64 \
     && aliyun_ver="3.0.150" \
     && ossutil_ver="1.7.6" \
     && curl -sL -o /aliyun-cli-linux-${aliyun_ver}-${aliyun_arch}.tgz https://github.com/aliyun/aliyun-cli/releases/download/v${aliyun_ver}/aliyun-cli-linux-${aliyun_ver}-${aliyun_arch}.tgz \
     && (cd /usr/local/bin ; tar xf /aliyun-cli-linux-${aliyun_ver}-${aliyun_arch}.tgz) \
     && rm /aliyun-cli-linux-${aliyun_ver}-${aliyun_arch}.tgz \
     && curl -sL -o /usr/local/bin/ossutil https://gosspublic.alicdn.com/ossutil/${ossutil_ver}/ossutil${ossutil_arch}?spm=a2c63.p38356.a3.3.44692454KkczI0  \
     && ln -s /usr/local/bin/ossutil /ossutil${ossutil_arch}?spm=a2c63.p38356.a3.3.44692454KkczI0 \
     && chmod 755 /usr/local/bin/ossutil \
     && apt-get clean && rm -rf /var/lib/apt/lists/* \
     && mkdir -p /root/.aws /root/.ssh /config
RUN : "Install firecracker specific binaries" \
     && arch="$(uname -m)" \
     && firecracker_ver="v1.1.4" \
     && release_url="https://github.com/firecracker-microvm/firecracker/releases" \
     && echo ${release_url}/download/${firecracker_ver}/firecracker-${firecracker_ver}-${arch}.tgz \
     && wget ${release_url}/download/${firecracker_ver}/firecracker-${firecracker_ver}-${arch}.tgz \
     && tar -xzv --no-same-owner -f firecracker-${firecracker_ver}-${arch}.tgz \
     && ln -s /release-${firecracker_ver}-${arch}/firecracker-${firecracker_ver}-${arch} /bin/firecracker

WORKDIR /gardenlinux/tests
