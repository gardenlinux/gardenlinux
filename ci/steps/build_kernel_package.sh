build_kernel_package(){
    set -ex

    repo_dir=$1
    pkg_names=$2

    # split string into an array
    echo "Input: ${pkg_names}"
    IFS=', ' read -r -a packages <<< "${pkg_names}"
    echo "Building kernel dependent packages: ${packages[@]}"

    if [ -z "$SOURCE_PATH" ]; then
    SOURCE_PATH="$(readlink -f ${repo_dir})"
    fi

    if [ -z "${packages}" ]; then
    echo "ERROR: no package name given"
    exit 1
    fi

    echo $(pwd)

    MANUALDIR=$(realpath $repo_dir/packages/manual)
    KERNELDIR=$(realpath $repo_dir/packages/kernel)

    export DEBFULLNAME="Garden Linux Maintainers"
    export DEBEMAIL="contact@gardenlinux.io"
    export BUILDIMAGE="gardenlinux/build-deb"
    export BUILDKERNEL="gardenlinux/build-kernel"
    export WORKDIR="/workspace"
    export CERTDIR=$(realpath $repo_dir/cert)
    echo "MANUALDIR: ${MANUALDIR}"
    echo "KERNELDIR: ${KERNELDIR}"
    echo "CERTDIR: ${CERTDIR}"
    echo "WORKDIR: ${WORKDIR}"

    # original makefile uses mounts, replace this by linking required dirs
    # to the expexted locations:
    # original: mount <gardenlinuxdir>/.packages but this does not exist so just create
    ln -s ${MANUALDIR} /workspace/manual
    ln -s /../Makefile.inside /workspace/Makefile
    echo "$(gpgconf --list-dir agent-socket)"
    mkdir -p /workspace/.gnupg
    ln -s $(gpgconf --list-dir agent-socket) /workspace/.gnupg/S.gpg-agent
    ln -s ${CERTDIR}/sign.pub /sign.pub
    ln -s ${CERTDIR}/Kernel.sign.full /kernel.full
    ln -s ${CERTDIR}/Kernel.sign.crt /kernel.crt
    ln -s ${CERTDIR}/Kernel.sign.key /kernel.key

    # originally this is called on docker startup
    gpg --import ${CERTDIR}/sign.pub

    echo "Checking disk begin end of kernel-packages build:"
    df -h
    sudo apt-get install --no-install-recommends -y wget quilt vim less

    export BUILDTARGET="${OUT_PATH:-/workspace/pool}"
    if [ ! -f "$BUILDTARGET" ]; then
    mkdir "$BUILDTARGET"
    fi

    for package in "${packages[@]}"
    do
    echo "Building now ${package}"
    pkg_build_script_path="${repo_dir}/packages/manual/${package}"
    echo "pkg_build_script_path: ${pkg_build_script_path}"

    if [ ! -f "${pkg_build_script_path}" ]; then
        echo "ERROR: Don't know how to build ${package}"
        exit 1
    fi

    pushd "/workspace"
    ${pkg_build_script_path}
    popd
    done
    echo "Checking disk usage end of kernel-packages build:"
    df -h
}