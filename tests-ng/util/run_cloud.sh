#!/usr/bin/env bash

set -eufo pipefail

cloud=
cloud_image=0
cloud_plan=0
only_cleanup=0
skip_cleanup=0
skip_tests=0
test_args=()
image_requirements=

while [ $# -gt 0 ]; do
	case "$1" in
	--cloud)
		cloud="$2"
		shift 2
		;;
	--cloud-image)
		cloud_image=1
		shift
		;;
	--cloud-plan)
		cloud_plan=1
		shift
		;;
	--only-cleanup)
		only_cleanup=1
		shift
		;;
	--skip-cleanup)
		skip_cleanup=1
		shift
		;;
	--skip-tests)
		skip_tests=1
		shift
		;;
	--test-args)
		# Split the second argument on spaces to handle multiple test arguments
		IFS=' ' read -ra args <<<"$2"
		test_args+=("${args[@]}")
		shift 2
		;;
	--image-requirements-file)
		image_requirements="$2"
		shift 2
		;;
	*)
		break
		;;
	esac
done

test_dist_dir="$1"
image="$2"
image_basename="$(basename -- "$image")"
image_name=${image_basename/.*/}
user_data_script=
util_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")")"
tf_dir="$util_dir/tf"
login_cloud_sh="$util_dir/login_cloud.sh"
uuid_file="$util_dir/.uuid"
if [ ! -f "$uuid_file" ]; then
	uuid=$(uuidgen | tr A-F a-f)
	echo "$uuid" >"$uuid_file"
else
	uuid=$(<"$uuid_file")
fi
seed=${uuid%%-*}
workspace="${image_name}-${seed}"

log_dir="$util_dir/../log"
log_file_log="cloud.test-ng.log"
log_file_junit="cloud.test-ng.xml"

mkdir -p "$log_dir"
test_args+=("--junit-xml=/run/gardenlinux-tests/tests/log/$log_file_junit")

# Extract test artifact name from image filename
test_artifact="$(basename "$image" | sed 's/-[0-9].*\.raw$//')"
test_type="cloud"
test_namespace="test-ng"

# Add pytest-metadata arguments
test_args+=("--metadata" "Artifact" "$test_artifact")
test_args+=("--metadata" "Type" "$test_type")
test_args+=("--metadata" "Namespace" "$test_namespace")

echo "📊  metadata: Artifact=$test_artifact, Type=$test_type, Namespace=$test_namespace"

# arch, uefi, secureboot, tpm2 are set in $image.requirements
arch=
uefi=
secureboot=
tpm2=
if [ -z "$image_requirements" ]; then
	# Only try to derive requirements file from image name if not using --cloud-image
	# When using --cloud-image, image_requirements is explicitly provided
	if ! ((cloud_image)); then
		image_requirements=${image//.raw/.requirements}
	fi
fi
if ((cloud_image)) && [ -z "$image_requirements" ]; then
	echo "you must provide '--image-requirements-file' when running with '--cloud-image'" >&2
	exit 1
fi
# shellcheck source=/dev/null
source "$image_requirements"

[ -n "$arch" ]
[ -n "$cloud" ]

cleanup() {
	get_logs || true
	if ! ((skip_cleanup)); then
		echo "⚙️  cleaning up cloud resources"
		(
			cd "${tf_dir}"
			tofu init -var-file "$image_name.tfvars"
			tofu workspace select "$workspace"
			tofu init -var-file "$image_name.tfvars"
			tofu destroy -var-file "$image_name.tfvars" --auto-approve
			tofu workspace select default
			tofu workspace delete "$workspace"
		)
	fi
}

get_logs() {
	"$login_cloud_sh" "$image_basename" "sudo cat /run/gardenlinux-tests/tests/log/$log_file_junit" >"$log_dir/$log_file_junit"
}

trap cleanup EXIT

case "$(uname -s)" in
Linux)
	os=linux
	;;
Darwin)
	os=darwin
	;;
*)
	echo "Operating System not supported"
	exit 1
	;;
esac

case "$(uname -m)" in
x86_64)
	arch=amd64
	;;
aarch64 | arm64)
	arch=arm64
	;;
*)
	echo "Arch not supported"
	exit 1
	;;
esac

tofuenv_dir="$tf_dir/.tofuenv"
PATH="$tofuenv_dir/bin:$PATH"
# in case we pass a GITHUB_TOKEN, we can work around rate limiting
export TOFUENV_GITHUB_TOKEN="${GITHUB_TOKEN:-}"
command -v tofuenv >/dev/null || {
	retry -d "1,2,5,10,30" git clone --depth=1 https://github.com/tofuutils/tofuenv.git "$tofuenv_dir"
	echo 'trust-tofuenv: yes' >"$tofuenv_dir/use-gpgv"
}
# go to tofu directory to automatically parse *.tf files
pushd "$tf_dir"
retry -d "1,2,5,10,30" tofuenv install latest-allowed
popd
tofu_version=$(find "$tf_dir/.tofuenv/versions" -mindepth 1 -maxdepth 1 -type d -printf "%f\n" | head -1)
tofuenv use "$tofu_version"

TF_CLI_CONFIG_FILE="$tf_dir/.terraformrc"
export TF_CLI_CONFIG_FILE
TOFU_PROVIDERS_CUSTOM="$tf_dir/.terraform/providers/custom"
TOFU_PROVIDER_AZURERM_VERSION="v4.41.0"
TOFU_PROVIDER_AZURERM_VERSION_LONG="${TOFU_PROVIDER_AZURERM_VERSION}-post1-secureboot2"
TOFU_PROVIDER_AZURERM_BIN="terraform-provider-azurerm_${TOFU_PROVIDER_AZURERM_VERSION}_${os}_${arch}"
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
	case "${os}_${arch}" in
	linux_amd64) checksum="$TOFU_PROVIDER_AZURERM_CHECKSUM_linux_amd64" ;;
	linux_arm64) checksum="$TOFU_PROVIDER_AZURERM_CHECKSUM_linux_arm64" ;;
	darwin_amd64) checksum="$TOFU_PROVIDER_AZURERM_CHECKSUM_darwin_amd64" ;;
	darwin_arm64) checksum="$TOFU_PROVIDER_AZURERM_CHECKSUM_darwin_arm64" ;;
	*)
		echo "Unsupported OS/arch combination: ${os}_${arch}" >&2
		exit 1
		;;
	esac
	echo "$checksum ${TOFU_PROVIDERS_CUSTOM}/terraform-provider-azurerm" >"${TOFU_PROVIDERS_CUSTOM}/checksum.txt"
	sha256sum -c "${TOFU_PROVIDERS_CUSTOM}/checksum.txt"
	chmod +x "${TOFU_PROVIDERS_CUSTOM}/terraform-provider-azurerm"
fi

ssh_private_key="$util_dir/../.ssh/id_ed25519_gl"
if [ ! -f "$ssh_private_key" ]; then
	mkdir -p "$(dirname "$ssh_private_key")"
	ssh-keygen -t ed25519 -f "$ssh_private_key" -N "" >/dev/null
fi

user_data_script="$(mktemp)"
cat >"$user_data_script" <<EOF
#!/usr/bin/env bash

systemctl enable --now ssh

mkdir /run/gardenlinux-tests
# disk attachment might take a while
for i in \$(seq 1 12); do
	mount /dev/disk/by-label/GL_TESTS /run/gardenlinux-tests && break
	sleep 10
done

if ! mountpoint /run/gardenlinux-tests; then
	exit 1
fi
mkdir -p /run/gardenlinux-tests/tests/log
EOF

if ((cloud_image)); then
	root_disk_path_var=""
	existing_root_disk_var="$image"
else
	root_disk_path_var="$(realpath -- "$image")"
	existing_root_disk_var=""
fi

cat >"${tf_dir}/$image_name.tfvars" <<EOF
root_disk_path        = "$root_disk_path_var"
test_disk_path        = "$(realpath -- "$test_dist_dir/dist.ext2.raw")"
ssh_public_key_path   = "$ssh_private_key.pub"
user_data_script_path = "$user_data_script"
existing_root_disk    = "$existing_root_disk_var"

image_requirements = {
  arch = "$arch"
  uefi = $uefi
  secureboot = $secureboot
  tpm2 = $tpm2
}

cloud_provider = "$cloud"

# provider_vars = {
#     ali = {
#     }
#     aws = {
#     }
# 	azure = {
# 	}
# 	gcp = {
# 	}
#     openstack = {
#     }
# }
EOF

if ((only_cleanup)); then
	exit 0 # triggers trap
fi

echo "⚙️  setting up cloud resources via OpenTofu"
if ((cloud_plan)); then
	tf_cmd=("plan")
else
	tf_cmd=("apply" "--auto-approve")
fi

(
	cd "${tf_dir}"
	tofu init -var-file "$image_name.tfvars"
	tofu workspace select -or-create "$workspace"
	tofu "${tf_cmd[@]}" -var-file "$image_name.tfvars"
)

if ! ((cloud_plan)); then
	vm_ip="$(cd "${tf_dir}" && tofu output --raw vm_ip)"
	ssh_user="$(cd "${tf_dir}" && tofu output --raw ssh_user)"

	echo -n "⚙️  waiting for VM ($vm_ip) to accept ssh connections"
	until "$login_cloud_sh" "$image_basename" true 2>/dev/null; do
		echo -n .
		sleep 1
	done

	if ! ((skip_tests)); then
		test_args+=(
			"--system-booted"
			"--allow-system-modifications"
			"--expected-users" "$ssh_user"
		)
		(
			# wait for cloud-init to finish
			"$login_cloud_sh" "$image_basename" "sudo systemctl is-system-running --wait || true"
			"$login_cloud_sh" "$image_basename" "sudo /run/gardenlinux-tests/run_tests ${test_args[*]@Q} 2>&1"
		) | tee "$log_dir/$log_file_log"
	fi
fi
