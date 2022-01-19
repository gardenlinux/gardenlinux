#!/bin/bash
set -euE Pipefail

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
GARDENLINUX_VERSION="$(${SCRIPTPATH}/../../bin/garden-version)"

pushd ${SCRIPTPATH}
echo '### create rootfs.tar.xz'
../../build.sh --features=oci,_slim . || :


echo '### build gardenlinux base image'
ROOTFS_PATH="oci-amd64-dev-local/rootfs.tar.xz"
if [ -e "${ROOTFS_PATH}" ]; then
  docker build --build-arg ROOTFS_PATH=${ROOTFS_PATH} -t gardenlinux/base:${GARDENLINUX_VERSION} .
else
  echo '### Error: ${ROOTFS_PATH} does not exist'
fi
popd
