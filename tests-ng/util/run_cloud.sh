#!/usr/bin/env bash

set -eufo pipefail

skip_cleanup=0
arch=
cloud=
cloud_image=0
use_scp=0

while [ $# -gt 0 ]; do
	case "$1" in
	--arch)
		arch="$2"
		shift 2
		;;
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
	--scp)
		use_scp=1
		shift
		;;
	*)
		break
		;;
	esac
done

[ -n "$arch" ]
[ -n "$cloud" ]

test_dist_dir="$1"
image="$2"
image_basename="$(basename -- "$image")"
user="admin"

user_data_script=
tf_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/tf")"

cleanup() {
	if ! ((skip_cleanup)); then
		echo "⚙️  cleaning up cloud resources"
		(
			cd "${tf_dir}"
			tofu workspace select "$image_basename"
			tofu destroy --auto-approve
			tofu workspace select default
			tofu workspace delete "$image_basename"
		)
	fi
}

trap cleanup EXIT

user_data_script="$(mktemp)"
if ((use_scp)); then
	cat >"$user_data_script" <<'EOF'
#!/usr/bin/env bash

systemctl stop sshguard
systemctl enable --now ssh
EOF
else
	cat >"$user_data_script" <<'EOF'
#!/usr/bin/env bash

systemctl stop sshguard
systemctl enable --now ssh

mkdir -p /var/tmp/gardenlinux-tests
mount /dev/disk/by-label/GL_TESTS /var/tmp/gardenlinux-tests
EOF
fi

if ((cloud_image)); then
	root_disk_path_var=""
	existing_root_disk_var="$image"
else
	root_disk_path_var="$(realpath -- "$image")"
	existing_root_disk_var=""
fi

if ((use_scp)); then
	use_scp_tf=true
else
	use_scp_tf=false
fi

cat >"${tf_dir}/terraform.tfvars" <<EOF
root_disk_path        = "$root_disk_path_var"
test_disk_path        = "$(realpath -- "$test_dist_dir/dist.raw")"
user_data_script_path = "$user_data_script"
existing_root_disk    = "$existing_root_disk_var"
use_scp             = ${use_scp_tf}

image_requirements = {
  arch = "$arch"
}

cloud_provider = "$cloud"
EOF

echo "⚙️  setting up cloud resources via OpenTofu"
(
	cd "${tf_dir}"
	tofu init
	tofu workspace select -or-create "$image_basename"
	tofu apply --auto-approve
)

vm_ip="$(cd "${tf_dir}" && tofu output --raw vm_ip)"
login_cloud_sh="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/login_cloud.sh")"
scp_to_cloud_sh="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/scp_to_cloud.sh")"

echo -n "⚙️  waiting for VM ($vm_ip) to accept ssh connections"
until "$login_cloud_sh" --user "$user" "$image_basename" true 2>/dev/null; do
	echo -n .
	sleep 1
done

if ((use_scp)); then
	checksum_expected="$(sha256sum "$test_dist_dir/dist.tar.gz" | awk '{print $1}')"
	checksum_actual="$($login_cloud_sh --user "$user" "$image_basename" 'sha256sum /var/tmp/gardenlinux-tests/dist.tar.gz' | awk '{print $1}' || echo false)"
	if [ "$checksum_expected" != "$checksum_actual" ]; then
		$login_cloud_sh --user "$user" "$image_basename" 'rm -f /var/tmp/gardenlinux-tests && mkdir -p /var/tmp/gardenlinux-tests'
		$scp_to_cloud_sh --user "$user" "$image_basename" "$test_dist_dir/dist.tar.gz" "/var/tmp/gardenlinux-tests/"
		$login_cloud_sh --user "$user" "$image_basename" 'cd /var/tmp/gardenlinux-tests && tar -xzf dist.tar.gz'
	fi
fi
"$login_cloud_sh" --user admin "$image_basename" sudo /var/tmp/gardenlinux-tests/run_tests --system-booted --expected-users admin
