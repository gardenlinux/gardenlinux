ARG build_base_image=gardenlinux/slim

FROM $build_base_image
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends make gettext openssl gnupg golang-cfssl efitools uuid-runtime
