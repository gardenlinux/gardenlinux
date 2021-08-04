build_image() {
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

    pwd
    echo "running build.."
    $(params.repo_dir)/bin/garden-build.sh \
        --arch $arch \
        --commitid $commitid \
        --suite $suite \
        --gardenversion $gardenversion \
        --features "${features}"
    ls -la "${OUT_FILE}"
    tar tf "${OUT_FILE}"
    if [ -f "${OUT_FILE}" ]; then
        echo "seems, like we might have succeeded?"
    else
        echo "no archive was created - see build log above for errors"
        exit 1
    fi
}