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
tf_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/tf")"

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
	if ! ((skip_cleanup)); then
		echo "⚙️  cleaning up cloud resources"
		(
			cd "${tf_dir}"
			tofu init -var-file "$image_name.tfvars"
			tofu workspace select "$image_name"
			tofu init -var-file "$image_name.tfvars"
			tofu destroy -var-file "$image_name.tfvars" --auto-approve
			tofu workspace select default
			tofu workspace delete "$image_name"
		)
	fi
}

trap cleanup EXIT

tofuenv_dir="$tf_dir/.tofuenv"
PATH="$tofuenv_dir/bin:$PATH"
command -v tofuenv >/dev/null || {
	git clone --depth=1 https://github.com/tofuutils/tofuenv.git "$tofuenv_dir"
	echo 'trust-tofuenv: yes' >"$tofuenv_dir/use-gpgv"
}
pushd "$tf_dir"
tofuenv install latest-allowed
popd
tofu_version="$(tofuenv list | head -1 | cut -d' ' -f2)"
tofuenv use "$tofu_version"

TF_CLI_CONFIG_FILE="$tf_dir/.terraformrc"
export TF_CLI_CONFIG_FILE
TOFU_PROVIDERS_CUSTOM="$tf_dir/.terraform/providers/custom"
TOFU_PROVIDER_AZURERM_URL="https://github.com/gardenlinux/terraform-provider-azurerm/releases/download/v4.41.0-post1-secureboot1/terraform-provider-azurerm"
TOFU_PROVIDER_AZURERM_CHECKSUM="d0724b2b33270dbb0e7946a4c125e78b5dd0f34697b74a08c04a1c455764262e"

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
	echo "$TOFU_PROVIDER_AZURERM_CHECKSUM ${TOFU_PROVIDERS_CUSTOM}/terraform-provider-azurerm" >"${TOFU_PROVIDERS_CUSTOM}/checksum.txt"
	sha256sum -c "${TOFU_PROVIDERS_CUSTOM}/checksum.txt"
	chmod +x "${TOFU_PROVIDERS_CUSTOM}/terraform-provider-azurerm"
fi

if ((only_cleanup)); then
	exit 0 # triggers trap
fi

ssh_private_key_path="$HOME/.ssh/id_ed25519_gl"
if [ ! -f "$ssh_private_key_path" ]; then
	mkdir -p "$(dirname "$ssh_private_key_path")"
	ssh-keygen -t ed25519 -f "$ssh_private_key_path" -N "" >/dev/null
fi

user_data_script="$(mktemp)"
cat >"$user_data_script" <<EOF
#!/usr/bin/env bash

systemctl stop sshguard
systemctl enable --now ssh

mkdir /run/gardenlinux-tests
mount /dev/disk/by-label/GL_TESTS /run/gardenlinux-tests
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
user_data_script_path = "$user_data_script"
existing_root_disk    = "$existing_root_disk_var"

image_requirements = {
  arch = "$arch"
  uefi = "$uefi"
  secureboot = "$secureboot"
  tpm2 = "$tpm2"
}

cloud_provider = "$cloud"

provider_vars = {
    ali = {
      ssh_user = "admin"
    }
    aws = {
        ssh_user = "admin"
    }
    gcp = {
      gcp_project_id = "$GCP_PROJECT_ID"
    }
    openstack = {
        ssh_user = "admin"
    }
}
EOF

echo "⚙️  setting up cloud resources via OpenTofu"
if ((cloud_plan)); then
	tf_cmd=("plan")
else
	tf_cmd=("apply" "--auto-approve")
fi

set -x

(
	cd "${tf_dir}"
	tofu init -var-file "$image_name.tfvars"
	tofu workspace select -or-create "$image_name"
	tofu "${tf_cmd[@]}" -var-file "$image_name.tfvars"
)

if ! ((cloud_plan)); then
	vm_ip="$(cd "${tf_dir}" && tofu output --raw vm_ip)"
	ssh_user="$(cd "${tf_dir}" && tofu output --raw ssh_user)"
	login_cloud_sh="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/login_cloud.sh")"

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
		"$login_cloud_sh" "$image_basename" sudo /run/gardenlinux-tests/run_tests "${test_args[*]@Q}"
	fi
fi
