
build_cfssl() {
    repo_dir=$1
    cfssl_fastpath=$2
    cfssl_dir=$3

    key_file="/workspace/gardenlinux_git/cert/private.key"

    if [[ -f "${key_file}" ]]; then
        gpg --import "${key_file}"
    fi

    mkdir -p "${repo_dir}/cert/cfssl"
    if [ "${cfssl_fastpath}" != "true" ]; then
    # slow-path build CFSSL from github:
    pushd "${cfssl_dir}"
    make
    mv bin/* "${repo_dir}/cert/cfssl"
    else
    mkdir -p "${repo_dir}/bin"
    pushd "${repo_dir}/bin"
    # fast-path copy binaries from CFSSL github release:
    cfssl_files=( cfssl-bundle_1.5.0_linux_amd64 \\
        cfssl-certinfo_1.5.0_linux_amd64 \\
        cfssl-newkey_1.5.0_linux_amd64 \\
        cfssl-scan_1.5.0_linux_amd64 \\
        cfssljson_1.5.0_linux_amd64 \\
        cfssl_1.5.0_linux_amd64 \\
        mkbundle_1.5.0_linux_amd64 \\
        multirootca_1.5.0_linux_amd64 \\
    )

    len2=`expr length _1.5.0_linux_amd64`
    for file in "${cfssl_files[@]}"; do
        len=`expr length $file`
        outname=${file:0:`expr $len - $len2`}
        wget --no-verbose -O $outname https://github.com/cloudflare/cfssl/releases/download/v1.5.0/${file}
        chmod +x $outname
    done
    mv * "${repo_dir}/cert/cfssl"
    fi
    # cleanup workspace to safe some valuable space
    popd
    rm -rf "${cfssl_dir}"
}