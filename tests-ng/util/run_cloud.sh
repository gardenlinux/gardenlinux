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
image_name="${image_basename%.*}"
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

if [ -n "${GITHUB_RUN_ID:-}" ] && [ -n "${GITHUB_RUN_NUMBER:-}" ]; then
	workspace="test-ng-${GITHUB_RUN_ID}-${GITHUB_RUN_NUMBER}-${image_name}-${seed}"
else
	workspace="test-ng-${image_name}-${seed}"
fi

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

# shellcheck source=/dev/null
source "$util_dir/install_tofu.sh"
install_tofu "$tf_dir"

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
	echo "⚙️  initializing terraform"
	tofu init -var-file "$image_name.tfvars"
	echo "⚙️  selecting workspace: $workspace"
	tofu workspace select -or-create "$workspace"
	echo "⚙️  running terraform ${tf_cmd[*]}"
	tofu "${tf_cmd[@]}" -var-file "$image_name.tfvars"
	echo "✅  terraform ${tf_cmd[*]} completed successfully"
)

if ! ((cloud_plan)); then
	echo "⚙️  getting terraform outputs"
	vm_ip="$(cd "${tf_dir}" && tofu output --raw vm_ip)"
	ssh_user="$(cd "${tf_dir}" && tofu output --raw ssh_user)"
	echo "📋  VM IP: $vm_ip, SSH User: $ssh_user"

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
			echo "⚙️  waiting for systemd to finish initialization (timeout: 10 minutes)"
			"$login_cloud_sh" "$image_basename" "timeout 600 sudo systemctl is-system-running --wait" || {
				echo "⚠️  systemctl is-system-running timed out or failed, checking system status"
				"$login_cloud_sh" "$image_basename" "sudo systemctl is-system-running" || true
				"$login_cloud_sh" "$image_basename" "sudo systemctl --failed --no-legend" || true
			}
			"$login_cloud_sh" "$image_basename" "sudo /run/gardenlinux-tests/run_tests ${test_args[*]@Q} 2>&1"
		) | tee "$log_dir/$log_file_log"
	fi
fi
