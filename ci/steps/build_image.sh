build_image() {
    set -Eeuo pipefail
    if [ -f '/workspace/skip_build' ]; then
        echo 'found /workspace/skip_build - skipping build'
        exit 0
    fi

    suite=$1
    gardenlinux_epoch=$2
    timestamp=$3
    features=$4,$5
    arch=$6
    commitid=$7
    gardenversion=$8

    echo "features: ${features}"
    ls -la /build
    export OUT_FILE="$(params.outfile)"
    export OUTPUT_DIR="${OUT_FILE}"

    repodir="$(params.repo_dir)"
    CERTDIR=$(realpath $repodir/cert)
    
    ln -s ${CERTDIR}/Kernel.sign.full /kernel.full
    ln -s ${CERTDIR}/Kernel.sign.crt /kernel.crt
    ln -s ${CERTDIR}/Kernel.sign.key /kernel.key

    pwd
    echo "running build.."
    $(params.repo_dir)/bin/garden-build.sh \
        --arch $arch \
        --commitid $commitid \
        --suite $suite \
        --gardenversion $gardenversion \
        --features "${features}"

    ls ${OUTPUT_DIR}
}
