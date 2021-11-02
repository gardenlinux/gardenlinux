
build_cfssl() {
    repo_dir=$1
    cfssl_dir=$2

    key_file="/workspace/gardenlinux_git/cert/private.key"

    if [[ -f "${key_file}" ]]; then
        gpg --import "${key_file}"
    fi

    mkdir -p "${repo_dir}/cert/cfssl"
    pushd "${cfssl_dir}"
    make
    mv bin/* "${repo_dir}/cert/cfssl"
    # cleanup workspace to safe some valuable space
    popd
    rm -rf "${cfssl_dir}"
}