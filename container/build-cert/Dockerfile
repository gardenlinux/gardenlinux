ARG build_base_image=gardenlinux/slim

FROM $build_base_image
ARG DEBIAN_FRONTEND=noninteractive
ARG	GARDENLINUX_MIRROR_KEY=/etc/apt/trusted.gpg.d/gardenlinux.asc
ARG	VERSION

COPY gardenlinux.asc $GARDENLINUX_MIRROR_KEY
RUN  chown root:root $GARDENLINUX_MIRROR_KEY \
        && chmod 644 $GARDENLINUX_MIRROR_KEY

RUN sed -i 's/deb.debian.org/cdn-aws.deb.debian.org/g' /etc/apt/sources.list
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates wget make gettext openssl libengine-pkcs11-openssl gnupg golang-cfssl efitools uuid-runtime awscli python3 python3-pip python3-crc32c git
RUN echo "deb [signed-by=$GARDENLINUX_MIRROR_KEY] https://repo.gardenlinux.io/gardenlinux $VERSION main" >> /etc/apt/sources.list  && \
	apt-get update && apt-get install -y --no-install-recommends libaws-sdk-cpp-dev aws-kms-pkcs11

RUN pip install git+https://github.com/awslabs/python-uefivars
