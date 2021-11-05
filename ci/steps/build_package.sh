build_package() {
    set -e
    set -x

    repo_dir=$1
    pkg_name=$2

    if [ -z "$SOURCE_PATH" ]; then
    SOURCE_PATH="$(readlink -f ${repo_dir})"
    fi

    if [ -z "${pkg_name}" ]; then
    echo "ERROR: no package name given"
    exit 1
    fi

    echo $(pwd)

    MANUALDIR=$(realpath ${repo_dir}/packages/manual)
    KERNELDIR=$(realpath ${repo_dir}/packages/kernel)

    export DEBFULLNAME="Garden Linux Maintainers"
    export DEBEMAIL="contact@gardenlinux.io"
    export BUILDIMAGE="gardenlinux/build-deb"
    export BUILDKERNEL="gardenlinux/build-kernel"
    export CERTDIR=$(realpath ${repo_dir}/cert)
    echo "MANUALDIR: ${MANUALDIR}"
    echo "KERNELDIR: ${KERNELDIR}"
    echo "CERTDIR: ${CERTDIR}"

    # original makefile uses mounts, replace this by linking required dirs
    # to the expexted locations:
    # original: mount <gardenlinuxdir>/.packages but this does not exist so just create
    ls -l ${CERTDIR}
    ln -s ${MANUALDIR} /workspace/manual
    ln -s /../Makefile.inside /workspace/Makefile

    ln -s ${CERTDIR}/sign.pub /sign.pub
    ln -s ${CERTDIR}/Kernel.sign.full /kernel.full
    ln -s ${CERTDIR}/Kernel.sign.crt /kernel.crt
    ln -s ${CERTDIR}/Kernel.sign.key /kernel.key

    # originally this is called on docker startup
    gpg --import ${CERTDIR}/sign.pub

    pkg_build_script_path="${repo_dir}/packages/manual/${pkg_name}"
    echo "pkg_build_script_path: ${pkg_build_script_path}"

    if [ ! -f "${pkg_build_script_path}" ]; then
    echo "ERROR: Don't know how to build ${pkg_name}"
    exit 1
    fi

    export BUILDTARGET="${OUT_PATH:-/workspace/pool}"
    if [ ! -f "$BUILDTARGET" ]; then
    mkdir "$BUILDTARGET"
    fi

    echo "Calling package-build script ${pkg_build_script_path}"
    ${pkg_build_script_path}
}