#!/usr/bin/env bash

set -eufo pipefail

cloud=
cloud_image=0
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
test_disk_path        = "$(realpath -- "$test_dist_dir/dist.raw")"
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
    aws = {
        ssh_user = "admin"
    }
}
EOF

echo "⚙️  setting up cloud resources via OpenTofu"
(
	cd "${tf_dir}"
	tofu init -var-file "$image_name.tfvars"
	tofu workspace select -or-create "$image_name"
	tofu apply -var-file "$image_name.tfvars" --auto-approve
)

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
