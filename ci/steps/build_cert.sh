build_cert() {
    repo_dir=$1
    # cfssl_fastpath=$2
    # cfssl_dir=$3

    key_file="${repo_dir}/cert/private.key"

    if [[ -f "${key_file}" ]]; then
        gpg --import "${key_file}"
    fi

    pushd "${repo_dir}/cert"
    make
    mkdir -p "${repo_dir}/certdir"
    cp --verbose Kernel.sign.full "${repo_dir}/certdir/kernel.full"
    cp --verbose Kernel.sign.crt "${repo_dir}/certdir/kernel.crt"
    cp --verbose Kernel.sign.key "${repo_dir}/certdir/kernel.key"
    cp --verbose sign.pub "${repo_dir}/certdir/sign.pub"
    cp --verbose root.ca.crt "${repo_dir}/certdir/root.ca.crt"
    cp --verbose root.ca.key "${repo_dir}/certdir/root.ca.crt"
}