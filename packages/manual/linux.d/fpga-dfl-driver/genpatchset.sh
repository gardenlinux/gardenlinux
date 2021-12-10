#!/usr/bin/env bash
set -euxo pipefail

workingDir="$(readlink -f "$(pwd)")"
srcDir="linux-dfl"
DFL_BRANCH="fpga-ofs-dev-5.10-lts"
KERNEL_VERSION="5.10.81"

git clone https://github.com/OPAE/linux-dfl.git ${srcDir}

pushd ${srcDir} || exit 1

    git remote add linux-stable git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git
    git fetch -t linux-stable
    git checkout ${DFL_BRANCH}
    git format-patch -o dfl_patches --first-parent --no-merges v${KERNEL_VERSION}..${DFL_BRANCH}
    mv dfl_patches ${workingDir}

popd ||exit 1

rm -rf ${srcDir}