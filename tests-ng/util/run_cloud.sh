#!/usr/bin/env bash

set -eufo pipefail

skip_cleanup=0
arch=
cloud=

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
		--skip-cleanup)
			skip_cleanup=1
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
image_name=${image_basename/.*/}

user_data_script=
tf_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/tf")"

cleanup() {
	[ -z "$user_data_script" ] || rm "$user_data_script"
	if ! ((skip_cleanup)); then
		echo "⚙️  cleaning up cloud resources"
		(
			cd "${tf_dir}"
			tofu workspace select "$image_name"
			tofu destroy -var-file "$image_name.tfvars" --auto-approve
			tofu workspace select default
			tofu workspace delete "$image_name"
		)
	fi
}

trap cleanup EXIT

user_data_script="$(mktemp)"
cat > "$user_data_script" << EOF
#!/usr/bin/env bash

systemctl stop sshguard
systemctl enable --now ssh

mkdir /run/gardenlinux-tests
mount /dev/disk/by-label/GL_TESTS /run/gardenlinux-tests
EOF

cat > "$tf_dir/$image_name.tfvars" << EOF
root_disk_path        = "$(realpath -- "$image")"
test_disk_path        = "$(realpath -- "$test_dist_dir/dist.ext2")"
user_data_script_path = "$user_data_script"

image_requirements = {
  arch = "$arch"
}

cloud_provider = "$cloud"
EOF

echo "⚙️  setting up cloud resources via OpenTofu"
(
	cd "${tf_dir}"
	tofu init
	tofu workspace select -or-create "$image_name"
	tofu apply -var-file "$image_name.tfvars" --auto-approve
)

vm_ip="$(cd "$tf_dir" && tofu output --raw vm_ip)"

echo -n "⚙️  waiting for VM ($vm_ip) to accept ssh connections"
until ssh -o ConnectTimeout=3 -o BatchMode=yes -o StrictHostKeyChecking=no "admin@$vm_ip" true 2>/dev/null; do
	echo -n .
	sleep 1
done

echo
ssh -o ConnectTimeout=3 -o BatchMode=yes -o StrictHostKeyChecking=no "admin@$vm_ip" sudo /run/gardenlinux-tests/run_tests --system-booted --expected-users admin
