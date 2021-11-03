build_cert() {
    repo_dir=$1
    build_cfssl=$2

    key_file="${repo_dir}/cert/private.key"
    cert_dir="${repo_dir}/cert"

    if [[ -f "${key_file}" ]]; then
        gpg --import "${key_file}"
    fi

    pushd "${cert_dir}"

    # in order to prevent downloading/building cfssl if it's already present
    # in the build image, create links to expected files before calling make
    if [[ "$(which cfssl)" ]] && [[ "$(which cfssljson)" ]]; then
        mkdir -p "cfssl/"
        ln -s "$(which cfssl)" "${cert_dir}/cfssl/cfssl"
        ln -s "$(which cfssljson)" "${cert_dir}/cfssl/cfssljson"
    fi

    make
}