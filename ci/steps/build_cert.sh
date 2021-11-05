build_cert() {
    repo_dir=$1

    key_file="${repo_dir}/cert/private.key"
    cert_dir="${repo_dir}/cert"

    if [[ -f "${key_file}" ]]; then
        gpg --import "${key_file}"
    fi

    pushd "${cert_dir}"

    # check if cfssl/cfssljson are present. They are required to create
    # the certificates.
    if [[ "$(which cfssl)" ]] && [[ "$(which cfssljson)" ]]; then
        mkdir -p "cfssl/"
        ln -s "$(which cfssl)" "${cert_dir}/cfssl/cfssl"
        ln -s "$(which cfssljson)" "${cert_dir}/cfssl/cfssljson"
    else
        echo "cfssl/cfssljson not found. Aborting"
        exit 1
    fi

    make
}