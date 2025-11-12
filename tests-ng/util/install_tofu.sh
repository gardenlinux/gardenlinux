#!/usr/bin/env bash

function die {
    # Perl like die() function.
    # https://billauer.co.il/blog/2024/08/bash-exit-with-error/
    # shellcheck disable=SC2086
    echo $1
    exit 1
}





install_tofu() {
	set -eufo pipefail
	local tf_dir="${1}"

    # Testing that the necesary biniaries are present at set indpendent of the path.
    case "$(uname -o)" in
        Darwin)
            FIND="/opt/homebrew/bin/gfind"
            RETRY="/opt/homebrew/bin/retry"
            test -x $FIND || die "Can't find find. Please install it with 'brew install findutils'"
            test -x $RETRY  || die "Can't find find. Please install it with 'brew install findutils'"
            ;;
        GNU/Linux)
            FIND="/usr/bin/find"
            RETRY="/usr/bin/retry"
            test -x $FIND || die "Can't find find. Please install it with 'apt-get install findutils'"
            test -x $RETRY  || die "Can't find find. Please install it with 'apt-get install findutils'"
            ;;
    esac

	case "$(uname -s)" in
	Linux)
		host_os=linux
		;;
	Darwin)
		host_os=darwin
		;;
	*)
		echo "Host operating system '$host_os' not supported"
		exit 1
		;;
	esac

	case "$(uname -m)" in
	x86_64)
		host_arch=amd64
		;;
	aarch64 | arm64)
		host_arch=arm64
		;;
	*)
		echo "Host architecture '$host_arch' not supported"
		exit 1
		;;
	esac

	tofuenv_dir="$tf_dir/.tofuenv"
	PATH="$tofuenv_dir/bin:$PATH"
	export PATH
	# in case we pass a GITHUB_TOKEN, we can work around rate limiting
	export TOFUENV_GITHUB_TOKEN="${GITHUB_TOKEN:-}"
	command -v tofuenv >/dev/null || {
		$RETRY -d "1,2,5,10,30" git clone --depth=1 https://github.com/tofuutils/tofuenv.git "$tofuenv_dir"
		echo 'trust-tofuenv: yes' >"$tofuenv_dir/use-gpgv"
	}
	# go to tofu directory to automatically parse *.tf files
	pushd "$tf_dir"
	$RETRY -d "1,2,5,10,30" tofuenv install latest-allowed
	popd
	tofu_version=$($FIND "$tf_dir/.tofuenv/versions" -mindepth 1 -maxdepth 1 -type d -printf "%f\n" | head -1)
	tofuenv use "$tofu_version"

	TF_CLI_CONFIG_FILE="$tf_dir/.terraformrc"
	export TF_CLI_CONFIG_FILE
	TOFU_PROVIDERS_CUSTOM="$tf_dir/.terraform/providers/custom"
	TOFU_PROVIDER_AZURERM_VERSION="v4.41.0"
	TOFU_PROVIDER_AZURERM_VERSION_LONG="${TOFU_PROVIDER_AZURERM_VERSION}-post1-secureboot2"
	TOFU_PROVIDER_AZURERM_BIN="terraform-provider-azurerm_${TOFU_PROVIDER_AZURERM_VERSION}_${host_os}_${host_arch}"
	TOFU_PROVIDER_AZURERM_URL="https://github.com/gardenlinux/terraform-provider-azurerm/releases/download/$TOFU_PROVIDER_AZURERM_VERSION_LONG/$TOFU_PROVIDER_AZURERM_BIN"
	TOFU_PROVIDER_AZURERM_CHECKSUM_linux_amd64="d0724b2b33270dbb0e7946a4c125e78b5dd0f34697b74a08c04a1c455764262e"
	TOFU_PROVIDER_AZURERM_CHECKSUM_linux_arm64="b5a5610bef03fcfd6b02b4da804a69cbca64e2c138c1fe943a09a1ff7b123ff7"
	TOFU_PROVIDER_AZURERM_CHECKSUM_darwin_amd64="0f4676ad2f0d16ec3e24f6ced1414b1f638c20da0a0b2c2b19e5bd279f0f1d32"
	TOFU_PROVIDER_AZURERM_CHECKSUM_darwin_arm64="bdda99a9139363676b1edf2f0371a285e1e1d9e9b9524de4f30b7c2b08224a86"

	cat >"$TF_CLI_CONFIG_FILE" <<EOF
provider_installation {
  dev_overrides {
    "hashicorp/azurerm" = "$TOFU_PROVIDERS_CUSTOM"
  }
  direct {}
}
EOF
	if [ ! -f "${TOFU_PROVIDERS_CUSTOM}/terraform-provider-azurerm" ] || ! sha256sum -c "${TOFU_PROVIDERS_CUSTOM}/checksum.txt" >/dev/null 2>&1; then
		echo "Downloading terraform-provider-azurerm"
		mkdir -p "${TOFU_PROVIDERS_CUSTOM}"
		curl -LO --create-dirs --output-dir "${TOFU_PROVIDERS_CUSTOM}" "${TOFU_PROVIDER_AZURERM_URL}"
		mv "${TOFU_PROVIDERS_CUSTOM}/${TOFU_PROVIDER_AZURERM_BIN}" "${TOFU_PROVIDERS_CUSTOM}/terraform-provider-azurerm"
		case "${host_os}_${host_arch}" in
		linux_amd64) checksum="$TOFU_PROVIDER_AZURERM_CHECKSUM_linux_amd64" ;;
		linux_arm64) checksum="$TOFU_PROVIDER_AZURERM_CHECKSUM_linux_arm64" ;;
		darwin_amd64) checksum="$TOFU_PROVIDER_AZURERM_CHECKSUM_darwin_amd64" ;;
		darwin_arm64) checksum="$TOFU_PROVIDER_AZURERM_CHECKSUM_darwin_arm64" ;;
		*)
			echo "Unsupported OS/arch combination: ${host_os}_${host_arch}" >&2
			exit 1
			;;
		esac
		echo "$checksum  terraform-provider-azurerm" >"${TOFU_PROVIDERS_CUSTOM}/checksum.txt"
		(cd "${TOFU_PROVIDERS_CUSTOM}" && sha256sum -c checksum.txt)
		chmod +x "${TOFU_PROVIDERS_CUSTOM}/terraform-provider-azurerm"
	fi
}

# If script is sourced, don't run main function automatically
if [ "${BASH_SOURCE[0]}" != "${0}" ]; then
	return 0
fi

install_tofu "${1}"
