build_cert() {
    repo_dir=$1

    key_file="${repo_dir}/cert/private.key"
    cert_dir="${repo_dir}/cert"

    if [[ -f "${key_file}" ]]; then
        gpg --import "${key_file}"
    fi

    pushd "${cert_dir}"
    make
}