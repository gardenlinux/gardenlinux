ARG build_base_image=gardenlinux/slim

FROM $build_base_image
ARG DEBIAN_FRONTEND=noninteractive

RUN sed -i 's/deb.debian.org/cdn-aws.deb.debian.org/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates wget make gettext openssl libengine-pkcs11-openssl gnupg golang-cfssl efitools uuid-runtime awscli
RUN arch="$(dpkg --print-architecture)" && \
	wget "https://gardenlinux-aws-kms-pkcs11.s3.eu-central-1.amazonaws.com/aws-sdk-cpp_$arch.deb" "https://gardenlinux-aws-kms-pkcs11.s3.eu-central-1.amazonaws.com/aws-kms-pkcs11_$arch.deb" && \
	apt-get install -y --no-install-recommends "./aws-sdk-cpp_$arch.deb" "./aws-kms-pkcs11_$arch.deb"
