#!/usr/bin/env bash

function die {
    # Perl like die() function.
    # https://billauer.co.il/blog/2024/08/bash-exit-with-error/
    # shellcheck disable=SC2086
    echo "💥 ${1}" >&2
    exit 1
}

function test_for_supported_os() {
    case "$(uname -s)" in
    Darwin)
        host_os=darwin
        ;;
    Linux)
        host_os=linux
        ;;
    *)
        die "Host operating system '$host_os' not supported"
        ;;
    esac
}

function test_for_supported_cpu_architecture() {
    case "$(uname -m)" in
    x86_64)
        host_arch=amd64
        ;;
    aarch64 | arm64)
        host_arch=arm64
        ;;
    *)
        die "Host architecture '$host_arch' not supported"
        ;;
    esac
}

function cleanup_custom_providers() {
    TF_CLI_CONFIG_FILE="$tf_dir/.terraformrc"
    rm -rf "$TF_CLI_CONFIG_FILE"
}

install_tofu() {
    set -eufo pipefail

    test_for_supported_os
    test_for_supported_cpu_architecture

    local tf_dir="${1}"
    tofuenv_dir="$tf_dir/.tofuenv"
    PATH="$tofuenv_dir/bin:$PATH"
    export PATH
    # in case we pass a GITHUB_TOKEN, we can work around rate limiting
    export TOFUENV_GITHUB_TOKEN="${GITHUB_TOKEN:-}"
    command -v tofuenv >/dev/null || {
        git clone --depth=1 https://github.com/tofuutils/tofuenv.git "$tofuenv_dir"
        echo 'trust-tofuenv: yes' >"$tofuenv_dir/use-gpgv"
    }
    # go to tofu directory to automatically parse *.tf files
    pushd "$tf_dir"
    tofuenv install latest-allowed
    tofuenv use latest-allowed
    popd

    cleanup_custom_providers
}

# If script is sourced, don't run main function automatically
if [ "${BASH_SOURCE[0]}" != "${0}" ]; then
    return 0
fi

install_tofu "${1}"
