#!/usr/bin/env bash

set -eufo pipefail

map_arch() {
	local arg="$1"
	if [ "$arg" = amd64 ]; then
		arg=x86_64
	elif [ "$arg" = arm64 ]; then
		arg=aarch64
	fi
	echo "$arg"
}

debug=0
ssh=0
skip_cleanup=0
skip_tests=0
test_args=()

while [ $# -gt 0 ]; do
	case "$1" in
	--debug)
		debug=1
		shift
		;;
	--ssh)
		ssh=1
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
	*)
		break
		;;
	esac
done

test_dist_dir="$1"
image="$2"
log_dir="$test_dist_dir/../log"
log_file_log="qemu.test-ng.log"
log_file_junit="qemu.test-ng.xml"

is_pxe_archive=0
if [[ "$image" == *.pxe.tar.gz ]]; then
	is_pxe_archive=1
fi

mkdir -p "$log_dir"
test_args+=("--junit-xml=/dev/virtio-ports/test_junit")

# arch, uefi, secureboot, tpm2 are set in $image.requirements
if ((is_pxe_archive)); then
	image_requirements=${image//.pxe.tar.gz/.requirements}
else
	image_requirements=${image//.raw/.requirements}
fi
# shellcheck source=/dev/null
source "$image_requirements"

[ -n "$arch" ]
arch="$(map_arch "$arch")"
[ -n "$uefi" ]
[ -n "$secureboot" ]
[ -n "$tpm2" ]

tmpdir=

cleanup() {
	if [ -n "${pxe_http_pid:-}" ]; then
		kill "$pxe_http_pid" 2>/dev/null || true
	fi
	get_logs
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

get_logs() {
	cp "$tmpdir/serial.log" "$log_dir/$log_file_log" || true
	cp "$tmpdir/junit.xml" "$log_dir/$log_file_junit" || true
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

if ((is_pxe_archive)); then
	echo "⚙️  detected PXE archive, preparing for PXE boot testing"
	pxe_extract_dir="$tmpdir/pxe_extracted"
	mkdir -p "$pxe_extract_dir"
	tar -xzf "$image" -C "$pxe_extract_dir"

	# TODO: get UKI to work
	# Verify required PXE components
	# if [ -f "$pxe_extract_dir/boot.efi" ]; then
	# 	# UKI case - boot.efi contains everything
	# 	echo "✅ Found UKI (boot.efi), will boot via iPXE"
	# 	required_files=("boot.efi")
	# else
	# Traditional case - require vmlinuz, initrd, root.squashfs
	required_files=("vmlinuz" "initrd" "root.squashfs")
	for file in "${required_files[@]}"; do
		if [ ! -f "$pxe_extract_dir/$file" ]; then
			echo "Error: Required PXE file '$file' not found in archive" >&2
			exit 1
		fi
	done
	echo "✅ PXE archive contains required files: ${required_files[*]}"
	# fi
fi

echo "⚙️  preparing test VM"

if ((is_pxe_archive)); then
	# For PXE testing, we'll use network boot instead of a disk image
	# Create a small empty disk for the test framework
	qemu-img create -q -f qcow2 "$tmpdir/disk.qcow" 1G
	echo "✅ PXE archive extracted, will use network boot"
else
	qemu-img create -q -f qcow2 -F raw -b "$(realpath -- "$image")" "$tmpdir/disk.qcow" 4G
fi

cat >"$tmpdir/fw_cfg-script.sh" <<EOF
#!/usr/bin/env bash

set -eufo pipefail

exec 1>/dev/virtio-ports/test_output
exec 2>&1
EOF

if ((ssh)); then
	ssh_private_key_path="$HOME/.ssh/id_ed25519_gl"
	ssh_public_key_path="${ssh_private_key_path}.pub"
	if [ ! -f "$ssh_private_key_path" ]; then
		mkdir -p "$(dirname "$ssh_private_key_path")"
		ssh-keygen -t ed25519 -f "$ssh_private_key_path" -N "" >/dev/null
	fi
	ssh_public_key=$(cat "$ssh_public_key_path")
	ssh_user="gardenlinux"
	cat >>"$tmpdir/fw_cfg-script.sh" <<EOF
systemctl enable --now ssh
useradd -U -m -G wheel -s /bin/bash $ssh_user
mkdir -p /home/$ssh_user/.ssh
chmod 700 /home/$ssh_user/.ssh
echo "$ssh_public_key" >> /home/$ssh_user/.ssh/authorized_keys
chown -R $ssh_user:$ssh_user /home/$ssh_user/.ssh
chmod 600 /home/$ssh_user/.ssh/authorized_keys
EOF
fi

if ! ((skip_cleanup)); then
	cat >>"$tmpdir/fw_cfg-script.sh" <<EOF
trap "poweroff -f > /dev/null 2>&1" EXIT
EOF
fi

cat >>"$tmpdir/fw_cfg-script.sh" <<'EOF'
mkdir /run/gardenlinux-tests
mount -o ro /dev/disk/by-label/GL_TESTS /run/gardenlinux-tests

cd /run/gardenlinux-tests
EOF

if [ "$arch" = x86_64 ]; then
	qemu_machine=q35
	qemu_cpu=qemu64
	qemu_tpm_dev=tpm-tis
fi

if [ "$arch" = aarch64 ]; then
	qemu_machine=virt
	qemu_cpu=cortex-a57
	qemu_tpm_dev=tpm-tis-device
fi

native_arch="$(map_arch "$(uname -m)")"

qemu_accel=tcg
if [ "$arch" = "$native_arch" ]; then
	if [ -w /dev/kvm ]; then
		qemu_accel=kvm
	elif [ "$(uname -s)" = Darwin ]; then
		if [ "$(sysctl -n kern.hv_support)" = 1 ]; then
			qemu_accel=hvf
		fi
	fi
fi

if ! ((skip_tests)); then
	test_args+=(
		"--system-booted"
		"--allow-system-modifications"
	)
	if [ "$qemu_accel" == "tcg" ]; then
		test_args+=("--skip-performance-metrics")
	fi
	if ((ssh)); then
		test_args+=("--expected-users" "$ssh_user")
	fi

	cat >>"$tmpdir/fw_cfg-script.sh" <<EOF
./run_tests ${test_args[*]@Q} 2>&1
EOF
fi

qemu_opts=(
	-machine "$qemu_machine"
	-cpu "$qemu_cpu"
	-m 4096
	-accel "$qemu_accel"
	-display none
	-serial stdio
	-drive "if=virtio,format=qcow2,file=$tmpdir/disk.qcow"
	-drive "if=virtio,format=raw,readonly=on,file=$test_dist_dir/dist.ext2.raw"
	-fw_cfg "name=opt/gardenlinux/config_script,file=$tmpdir/fw_cfg-script.sh"
	-chardev "file,id=test_output,path=$tmpdir/serial.log"
	-chardev "file,id=test_junit,path=$tmpdir/junit.xml"
	-device virtio-serial
	-device "virtserialport,chardev=test_output,name=test_output"
	-device "virtserialport,chardev=test_junit,name=test_junit"
	-device "virtio-net-pci,netdev=net0"
)

if ((debug)); then
	qemu_opts+=(
		-display gtk
	)
else
	qemu_opts+=(
		-display none
	)
fi

if ((is_pxe_archive)); then
	qemu_opts+=(
		-boot order=nc
	)
fi

if [ "$uefi" = "true" ] || [ "$arch" = aarch64 ]; then
	cp "$test_dist_dir/edk2-qemu-$arch-code" "$tmpdir/edk2-qemu-code"
	cp "$test_dist_dir/edk2-qemu-$arch-vars" "$tmpdir/edk2-qemu-vars"
	if [ "$arch" = aarch64 ]; then
		truncate -s 64M "$tmpdir/edk2-qemu-code"
		truncate -s 64M "$tmpdir/edk2-qemu-vars"
	fi
	qemu_opts+=(
		-drive "if=pflash,unit=0,format=raw,readonly=on,file=$tmpdir/edk2-qemu-code"
		-drive "if=pflash,unit=1,format=raw,file=$tmpdir/edk2-qemu-vars"
	)
fi

if [ "$tpm2" = "true" ]; then
	qemu_opts+=(
		-chardev "socket,id=chrtpm,path=$tmpdir/swtpm.sock"
		-tpmdev "emulator,id=tpm0,chardev=chrtpm"
		-device "$qemu_tpm_dev,tpmdev=tpm0"
	)
	swtpm socket --tpmstate backend-uri="file://$tmpdir/swtpm.permall" --ctrl type=unixio,path="$tmpdir/swtpm.sock" --tpm2 --daemon --terminate
fi

if ((is_pxe_archive)); then
	# Set up HTTP server for PXE boot
	http_dir="$tmpdir/http"
	mkdir -p "$http_dir"

	# TODO: get UKI to work
	# Copy PXE files to HTTP directory
	# if [ -f "$pxe_extract_dir/initrd.unified" ]; then
	#	# UKI case - copy initrd.unified and vmlinuz
	#	cp "$pxe_extract_dir/initrd.unified" "$http_dir/"
	#	cp "$pxe_extract_dir/vmlinuz" "$http_dir/"
	# else
	# Traditional case - copy vmlinuz, initrd, root.squashfs
	cp "$pxe_extract_dir/vmlinuz" "$http_dir/"
	cp "$pxe_extract_dir/initrd" "$http_dir/"
	cp "$pxe_extract_dir/root.squashfs" "$http_dir/"
	# fi

	# TODO: get UKI to work
	# Create iPXE script for booting
	# if [ -f "$pxe_extract_dir/initrd.unified" ]; then
	# 	echo "✅ Found initrd.unified (UKI), will boot via iPXE"
	# 	# Create iPXE script to boot boot.efi directly
	# 	cat >"$http_dir/boot.ipxe" <<'EOF'
	# #!ipxe
	# dhcp
	# set base-url http://10.0.2.2:8080
	# kernel ${base-url}/vmlinuz gl.ovl=/:tmpfs gl.live=1 ip=dhcp console=ttyS0 console=tty0 earlyprintk=ttyS0 consoleblank=0
	# initrd ${base-url}/initrd.unified
	# boot
	# EOF
	# else
	echo "✅ Using traditional vmlinuz/initrd boot via iPXE"
	# Create iPXE script for traditional vmlinuz/initrd boot
	cat >"$http_dir/boot.ipxe" <<'EOF'
#!ipxe
dhcp
set base-url http://10.0.2.2:8080
kernel ${base-url}/vmlinuz gl.ovl=/:tmpfs gl.url=${base-url}/root.squashfs gl.live=1 ip=dhcp console=ttyS0 console=tty0 earlyprintk=ttyS0 consoleblank=0
initrd ${base-url}/initrd
boot
EOF
	# fi

	# Start HTTP server for serving the files
	python3 -m http.server 8080 --directory "$http_dir" >/dev/null 2>&1 &
	http_pid=$!

	# Store HTTP server PID for cleanup
	pxe_http_pid=$http_pid

	if ((ssh)); then
		qemu_opts+=(
			-netdev "user,id=net0,hostfwd=tcp::2222-:22,tftp=$http_dir,bootfile=boot.ipxe"
		)
	else
		qemu_opts+=(
			-netdev "user,id=net0,tftp=$http_dir,bootfile=boot.ipxe"
		)
	fi

elif ((ssh)); then
	qemu_opts+=(
		-netdev "user,id=net0,hostfwd=tcp::2222-:22"
	)
else
	qemu_opts+=(
		-netdev "user,id=net0"
	)
fi

echo "🚀  starting test VM"

if ((skip_cleanup)); then
	# The following command starts the QEMU VM and pipes its output through sed to clean up the console output:
	# - s/\x1b\][0-9]*\x07//g      : Removes OSC (Operating System Command) escape sequences (e.g., title changes).
	# - s/\x1b[\[0-9;!?=]*[a-zA-Z]//g : Removes CSI (Control Sequence Introducer) ANSI escape codes (e.g., colors, cursor moves).
	# - s/\t/    /g                : Replaces tabs with four spaces for better readability.
	# - s/[^[:print:]]//g          : Removes any remaining non-printable characters.
	"qemu-system-$arch" "${qemu_opts[@]}" | stdbuf -i0 -o0 sed 's/\x1b\][0-9]*\x07//g;s/\x1b[\[0-9;!?=]*[a-zA-Z]//g;s/\t/    /g;s/[^[:print:]]//g' &
	sleep 5
	tail -f "$tmpdir/serial.log"
else
	"qemu-system-$arch" "${qemu_opts[@]}" | stdbuf -i0 -o0 sed 's/\x1b\][0-9]*\x07//g;s/\x1b[\[0-9;!?=]*[a-zA-Z]//g;s/\t/    /g;s/[^[:print:]]//g'
	cat "$tmpdir/serial.log"
fi

# TODO: find a better way to check if the tests failed
! (tail -n1 "$tmpdir/serial.log" | grep failed >/dev/null)
