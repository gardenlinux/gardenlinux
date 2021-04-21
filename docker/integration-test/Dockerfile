FROM gardenlinux/slim
ENV	DEBIAN_FRONTEND noninteractive
ENV SHELL /bin/bash
RUN	apt-get update \
     &&	apt-get install -y --no-install-recommends \
		curl \
		unzip \
        ca-certificates \
        less \
        apt-transport-https gnupg \
        pipenv \
        vim-tiny \
     && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
     && unzip awscliv2.zip \
     && ./aws/install \
     && rm -rf ./aws \
	 && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
     && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
     && apt-get update \
     && apt-get install -y google-cloud-sdk \
     && curl -sL https://aka.ms/InstallAzureCLIDeb | bash \
     &&	rm -rf /var/lib/apt/lists/*

WORKDIR	/tmp
