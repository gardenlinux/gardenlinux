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
util_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")")"
log_dir="$util_dir/../log"
log_file_log="qemu.test.log"
log_file_junit="qemu.test.xml"

is_pxe_archive=0
if [[ "$image" == *.pxe.tar.gz ]]; then
	is_pxe_archive=1
fi

is_iso=0
if [[ "$image" == *.iso ]]; then
	is_iso=1
fi

is_openstack=0
if [[ "$image" =~ ^.*openstack-.*$ ]]; then
	is_openstack=1
fi

mkdir -p "$log_dir"
test_args+=("--junit-xml=/dev/virtio-ports/test_junit")

# Extract test artifact name from image filename
if ((is_pxe_archive)); then
	test_artifact="$(basename "$image" | sed 's/-[0-9].*\.pxe\.tar\.gz$//')"
elif ((is_iso)); then
	test_artifact="$(basename "$image" | sed 's/-[0-9].*\.iso$//')"
else
	test_artifact="$(basename "$image" | sed 's/-[0-9].*\.raw$//')"
fi
test_type="qemu"
test_namespace="test"

# Add pytest-metadata arguments
test_args+=("--metadata" "Artifact" "$test_artifact")
test_args+=("--metadata" "Type" "$test_type")
test_args+=("--metadata" "Namespace" "$test_namespace")

echo "📊  metadata: Artifact=$test_artifact, Type=$test_type, Namespace=$test_namespace"

# arch, uefi, secureboot, tpm2, autoinstall are set in $image.requirements
if ((is_pxe_archive)); then
	image_requirements=${image//.pxe.tar.gz/.requirements}
elif ((is_iso)); then
	image_requirements=${image//.iso/.requirements}
else
	image_requirements=${image//.raw/.requirements}
fi
# shellcheck source=/dev/null
source "$image_requirements"

# TODO: remove after https://github.com/gardenlinux/builder/pull/148 is merged
autoinstall=false
if [[ "$image" =~ ^.*_autoinstall.*$ ]]; then
	autoinstall=true
fi

[ -n "$autoinstall" ]
[ -n "$arch" ]
arch="$(map_arch "$arch")"
[ -n "$uefi" ]
[ -n "$secureboot" ]
[ -n "$tpm2" ]

# Convert string booleans to numeric for arithmetic context
[ "$autoinstall" = "true" ] && autoinstall=1 || autoinstall=0

echo "⚙️  autoinstall detection: autoinstall=$autoinstall, is_iso=$is_iso, is_pxe=$is_pxe_archive"

tmpdir=

bg_pids=()

cleanup() {
	# Kill any background processes
	for pid in "${bg_pids[@]}"; do
		kill "$pid" 2>/dev/null || true
		wait "$pid" 2>/dev/null || true
	done
	bg_pids=()

	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}
trap cleanup EXIT

tmpdir="$(mktemp -d)"

if ((is_pxe_archive)); then
	echo "⚙️  detected PXE archive, preparing for PXE boot testing"
	pxe_extract_dir="$tmpdir/pxe_extracted"
	mkdir -p "$pxe_extract_dir"
	tar -xzf "$image" -C "$pxe_extract_dir"

	# Detect boot mode: UKI vs traditional
	is_uki=0
	if [ -f "$pxe_extract_dir/boot.efi" ]; then
		is_uki=1
		echo "✅ Found UKI (boot.efi), will use UEFI boot"
	fi

	# Determine required files based on boot mode
	if ((is_uki)); then
		required_files=("boot.efi" "root.squashfs")
		# vmlinuz/initrd are optional for UKI mode but useful for debugging
	else
		required_files=("vmlinuz" "initrd" "cmdline" "root.squashfs")
	fi

	for file in "${required_files[@]}"; do
		if [ ! -f "$pxe_extract_dir/$file" ]; then
			echo "Error: Required PXE file '$file' not found in archive" >&2
			exit 1
		fi
	done
	echo "✅ PXE archive contains required files: ${required_files[*]}"
fi

echo "⚙️  preparing test VM"

./util/metadata-server.py >/dev/null 2>&1 &
bg_pids+=("$!")
echo "✅ Started metadata server on 127.0.0.1:8181"

if ((is_pxe_archive)) || ((is_iso)); then
	qemu-img create -q -f qcow2 "$tmpdir/disk.qcow" 4G
else
	qemu-img create -q -f qcow2 -F raw -b "$(realpath -- "$image")" "$tmpdir/disk.qcow" 4G
fi

cat >"$tmpdir/fw_cfg-script.sh" <<EOF
#!/usr/bin/env bash

set -euf
set -x
EOF

# Conditionally stop serial-getty BEFORE exec redirect (only when SSH is enabled)
if ((ssh)); then
	cat >>"$tmpdir/fw_cfg-script.sh" <<'EOF'

# Stop serial-getty to get exclusive access to serial console for test output
# This allows our script output to reach QEMU's serial capture instead of being swallowed by getty
systemctl stop serial-getty@ttyS0.service 2>/dev/null || true
EOF
fi

cat >>"$tmpdir/fw_cfg-script.sh" <<EOF
# Send all output to console so it appears on
# the QEMU serial output (and thus in logs).
exec >/dev/console
exec 2>&1

# Redirect all output directly to serial console
exec > /dev/ttyS0 2>&1

echo "=== FW_CFG Script started at $(date) ==="
echo "=== Script PID: $$ ==="
echo "=== Current boot: $([ -f /.installed ] && echo 'INSTALLED SYSTEM' || echo 'LIVE SYSTEM') ==="

# Set up error trap
trap 'echo "❌ ERROR: Script failed at line $LINENO with exit code $?"' ERR
EOF

# Set up SSH user
if ((ssh)); then
	ssh_private_key="$util_dir/../.ssh/id_ed25519_gl"
	ssh_public_key="$ssh_private_key.pub"
	if [ ! -f "$ssh_private_key" ]; then
		mkdir -p "$(dirname "$ssh_private_key")"
		ssh-keygen -t ed25519 -f "$ssh_private_key" -N "" >/dev/null
	fi
	ssh_public_key=$(cat "$ssh_public_key")
	ssh_user="gardenlinux"
	# Ensure /home exists (live media squashfs may not have it, but tmpfs overlay is writable)
	cat >>"$tmpdir/fw_cfg-script.sh" <<EOF
mkdir -p /home
systemctl enable --now ssh
useradd -U -m -G wheel -s /bin/bash $ssh_user || true
mkdir -p /home/$ssh_user/.ssh
chmod 700 /home/$ssh_user/.ssh
echo "$ssh_public_key" >> /home/$ssh_user/.ssh/authorized_keys
chown -R $ssh_user:$ssh_user /home/$ssh_user/.ssh
chmod 600 /home/$ssh_user/.ssh/authorized_keys
EOF
fi

if ! ((skip_cleanup)); then
	if ((autoinstall && (is_iso || is_pxe_archive))); then
		# For autoinstall, only set poweroff trap on the installed system.
		# On the live boot we exit early and let gl-autoinstall.service handle the reboot.
		cat >>"$tmpdir/fw_cfg-script.sh" <<'EOF'
# Only poweroff on exit if this is the installed system (post-install boot).
# /.installed is written by install.sh into the installed root only.
# The former "|| ! mountpoint -q /run/rootfs" heuristic misfired on ISO live
# (which uses /run/rootfsbase, not /run/rootfs), arming the trap prematurely.
if [ -f /.installed ]; then
	trap "poweroff -f > /dev/null 2>&1" EXIT
fi
EOF
	else
		# For non-autoinstall, always poweroff on exit
		cat >>"$tmpdir/fw_cfg-script.sh" <<EOF
trap "poweroff -f > /dev/null 2>&1" EXIT
EOF
	fi
fi

# ISO autoinstall: let gl-autoinstall.service handle the installation
# The fw_cfg script only needs to exit on first boot and run tests on second boot
if ((autoinstall && is_iso)); then
	cat >>"$tmpdir/fw_cfg-script.sh" <<'EOF'
# On ISO live system, let gl-autoinstall.service handle the install and reboot
if ! [ -f /.installed ]; then
	echo "=== FIRST BOOT: Waiting for gl-autoinstall.service to complete installation ==="
	exit 0
fi
EOF
fi

# PXE autoinstall: let gl-autoinstall.service handle the installation
# The fw_cfg script only needs to exit on first boot and run tests on second boot
if ((autoinstall && is_pxe_archive)); then
	cat >>"$tmpdir/fw_cfg-script.sh" <<'EOF'
# On PXE live system, let gl-autoinstall.service handle the install and reboot
if ! [ -f /.installed ]; then
	echo "=== FIRST BOOT: Waiting for gl-autoinstall.service to complete installation ==="
	exit 0
fi
EOF
fi

if ! ((skip_tests)); then
	if ((autoinstall)); then
		# For autoinstall (ISO or PXE), only run tests on the installed system (post-install boot)
		cat >>"$tmpdir/fw_cfg-script.sh" <<'EOF'
if [ -f /.installed ]; then
	echo "=== SECOND BOOT: Preparing to run tests ===" | tee /dev/console
	mkdir /run/gardenlinux-tests
	mount -o ro /dev/disk/by-label/GL_TESTS /run/gardenlinux-tests
	echo "=== Tests mounted, starting test execution ===" | tee /dev/console

	cd /run/gardenlinux-tests
EOF
	else
		# For non-autoinstall, run tests immediately
		cat >>"$tmpdir/fw_cfg-script.sh" <<'EOF'
mkdir /run/gardenlinux-tests
echo "⚙️  Mounting test directory..."
mount -o ro /dev/disk/by-label/GL_TESTS /run/gardenlinux-tests
echo "️⚙️  Changing to test directory..."
cd /run/gardenlinux-tests
EOF
	fi
fi

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

# aarch64 virt machine does not support the legacy BIOS boot-device-list
# (-boot order/once) used by SeaBIOS/x86.  Use per-device bootindex= instead.
use_bootindex=0
if [ "$arch" = aarch64 ]; then
	use_bootindex=1
fi

native_arch="$(map_arch "$(uname -m)")"

qemu_accel=tcg
if [ "$arch" = "$native_arch" ]; then
	if [ -w /dev/kvm ]; then
		qemu_accel=kvm
	elif [ "$(uname -s)" = Darwin ]; then
		if [ "$(sysctl -n kern.hv_support)" = 1 ]; then
			qemu_accel=hvf
			qemu_cpu=host
		fi
	fi
fi

if ! ((skip_tests)); then
	test_args+=(
		"--system-booted"
		"--allow-system-modifications"
	)
	# skip performance metrics when no acceleration is availale or being run in a github runner
	if [[ "$qemu_accel" == "tcg" || (-v RUNNER_ENVIRONMENT && "$RUNNER_ENVIRONMENT" == github-hosted ) ]]; then
		test_args+=("--skip-performance-metrics")
	fi
	if ((ssh)); then
		test_args+=("--expected-users" "$ssh_user")
	fi

	cat >>"$tmpdir/fw_cfg-script.sh" <<'EOF'
echo "⚙️  waiting for systemd to finish initialization (timeout: 10 minutes)"
timeout 600 systemctl is-system-running --wait || {
	echo "⚠️  systemctl is-system-running timed out or failed, checking system status"
	systemctl is-system-running || true
	systemctl --failed --no-legend || true
}
EOF

	cat >>"$tmpdir/fw_cfg-script.sh" <<EOF
PYTHONUNBUFFERED=1 ./run_tests ${test_args[*]@Q} 2>&1
EOF

	# Close the conditional block for autoinstall tests
	if ((autoinstall)); then
		cat >>"$tmpdir/fw_cfg-script.sh" <<'EOF'
fi
EOF
	fi
fi

# On aarch64 PXE, set bootindex=0 on the network device so EDK2 tries network
# first.  On all other arch/boot-type combinations, no bootindex is needed here.
net_device="virtio-net-pci,netdev=net0"
if ((is_pxe_archive && use_bootindex)); then
	net_device="virtio-net-pci,netdev=net0,bootindex=0"
fi

qemu_opts=(
	-machine "$qemu_machine"
	-cpu "$qemu_cpu"
	-m 4096
	-accel "$qemu_accel"
	-display none
	-serial stdio
	-fw_cfg "name=opt/gardenlinux/config_script,file=$tmpdir/fw_cfg-script.sh"
	-chardev "file,id=test_junit,path=$log_dir/$log_file_junit"
	-device virtio-serial
	-device "virtserialport,chardev=test_junit,name=test_junit"
	-device "$net_device"
)

# Add the main disk (boot disk for raw/PXE, install target vda for ISO).
# On aarch64, split into an explicit device so we can attach bootindex=1;
# if=virtio shorthand does not accept bootindex.
if ((use_bootindex)); then
	qemu_opts+=(
		-drive "if=none,id=bootdisk,format=qcow2,file=$tmpdir/disk.qcow"
		-device "virtio-blk-pci,drive=bootdisk,bootindex=1"
	)
else
	qemu_opts+=(
		-drive "if=virtio,format=qcow2,file=$tmpdir/disk.qcow"
	)
fi

if ! ((skip_tests)); then
	qemu_opts+=(
		-drive "if=virtio,format=raw,readonly=on,file=$test_dist_dir/dist.ext2.raw"
	)
fi

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
	# Boot from network on first boot only; subsequent reboots fall through to disk.
	#
	# x86_64 (SeaBIOS / EDK2 q35): -boot once=n,order=c is honoured for the very
	# first boot.  After the installer writes EFI boot entries into the persistent
	# edk2-qemu-vars pflash, reboots pick the on-disk loader from NVRAM.
	#
	# aarch64 (EDK2 virt): the virt machine has no legacy BIOS boot-device-list,
	# so -boot once/order is not supported and causes QEMU to abort.  Instead we
	# use per-device bootindex= properties: bootindex=0 on virtio-net (try network
	# first) and bootindex=1 on the boot disk (fallback).  After the installer
	# writes NVRAM boot entries, subsequent reboots follow NVRAM and pick the
	# on-disk loader, not the network.  EDK2 aarch64 ships with the EFI PXE/HTTP
	# stack and loads boot.ipxe from TFTP the same way x86_64 UEFI does.
	if ! ((use_bootindex)); then
		qemu_opts+=(
			-boot "once=n,order=c"
		)
	fi
elif ((is_iso)); then
	# For ISO testing, boot from CDROM
	# WORKAROUND: The dracut initrd in the ISO doesn't load ahci driver automatically
	# Use SCSI CD-ROM attached to virtio-scsi controller for better compatibility
	# Boot from CD-ROM on first boot only; reboots fall through to disk.
	#
	# x86_64: -boot once=d,order=c is used for the one-shot CD-ROM first boot.
	# aarch64: -boot is not supported; bootindex=0 on the scsi-cd device is used.
	if ((use_bootindex)); then
		qemu_opts+=(
			-device "virtio-scsi-pci,id=scsi"
			-drive "id=cd0,if=none,format=raw,readonly=on,media=cdrom,file=$(realpath -- "$image")"
			-device "scsi-cd,drive=cd0,bus=scsi.0,bootindex=0"
		)
	else
		qemu_opts+=(
			-boot "once=d,order=c"
			-device "virtio-scsi-pci,id=scsi"
			-drive "id=cd0,if=none,format=raw,readonly=on,media=cdrom,file=$(realpath -- "$image")"
			-device "scsi-cd,drive=cd0,bus=scsi.0"
		)
	fi
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

	# Always serve root.squashfs
	cp "$pxe_extract_dir/root.squashfs" "$http_dir/"

	if ((is_uki)); then
		echo "✅ Setting up UKI boot"

		# Copy UKI for UEFI boot
		cp "$pxe_extract_dir/boot.efi" "$http_dir/"

		if ((autoinstall)); then
			# Serve ignition config
			ignition_json_source="$util_dir/ignition.json"
			if [ ! -f "$ignition_json_source" ]; then
				echo "❌ Error: ignition.json not found at $ignition_json_source" >&2
				exit 1
			fi
			cp "$ignition_json_source" "$http_dir/ignition.json"
			echo "✅ Copied ignition.json for PXE installation"
		fi

		# Create iPXE script to chainload UKI
		cat >"$http_dir/boot.ipxe" <<'EOF'
#!ipxe
dhcp
set base-url http://10.0.2.2:8080
chain ${base-url}/boot.efi
EOF

	else
		echo "✅ Using traditional vmlinuz/initrd boot via iPXE"

		# Copy traditional boot files
		cp "$pxe_extract_dir/vmlinuz" "$http_dir/"
		cp "$pxe_extract_dir/initrd" "$http_dir/"

		if ((autoinstall)); then
			ignition_json_source="$util_dir/ignition.json"
			if [ ! -f "$ignition_json_source" ]; then
				echo "❌ Error: ignition.json not found at $ignition_json_source" >&2
				exit 1
			fi
			cp "$ignition_json_source" "$http_dir/ignition.json"
			echo "✅ Copied ignition.json for PXE installation"

			cat >"$http_dir/boot.ipxe" <<EOF
#!ipxe
dhcp
set base-url http://10.0.2.2:8080
kernel \${base-url}/vmlinuz $(cat "$pxe_extract_dir/cmdline") gl.url=http://10.0.2.2:8080/root.squashfs ignition.firstboot=1 ignition.config.url=http://10.0.2.2:8080/ignition.json ignition.platform.id=metal
initrd \${base-url}/initrd
boot
EOF
		else
			cat >"$http_dir/boot.ipxe" <<EOF
#!ipxe
dhcp
set base-url http://10.0.2.2:8080
kernel \${base-url}/vmlinuz $(cat "$pxe_extract_dir/cmdline") gl.url=http://10.0.2.2:8080/root.squashfs
initrd \${base-url}/initrd
boot
EOF
		fi
	fi

	# Start HTTP server for serving files
	python3 -m http.server 8080 --directory "$http_dir" >/dev/null 2>&1 &
	bg_pids+=("$!")

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
		-netdev "user,id=net0,net=169.254.169.0/24,dhcpstart=169.254.169.9,hostfwd=tcp::2222-:22,guestfwd=tcp:169.254.169.254:80-cmd:socat - TCP:127.0.0.1:8181"
	)
else
	qemu_opts+=(
		-netdev "user,id=net0,net=169.254.169.0/24,dhcpstart=169.254.169.9,guestfwd=tcp:169.254.169.254:80-cmd:socat - TCP:127.0.0.1:8181"
	)
fi

echo "🚀  starting test VM"

# Run QEMU and stream its serial output:
# - Raw output (with colors) goes to the console for better readability
# - Cleaned output (without problematic escape sequences) goes to the log file
# The sed cleaning removes:
# - OSC escape sequences (e.g., title changes that can clutter logs) - s/\x1b\][0-9]*\x07//g
# - CSI escape codes (colors, cursor moves, screen clears, etc.) - s/\x1b[\[0-9;!?=]*[a-zA-Z]//g
# - Tabs are replaced with spaces for better log readability - s/\t/    /g
# - Non-printable characters that might cause issues in log files - s/[^[:print:]]//g
# Colors are preserved in console output but removed from log file
run_qemu() {
	local label="$1"
	shift
	local -a opts=("$@")

	echo "$label"
	"qemu-system-$arch" "${opts[@]}" | stdbuf -i0 -o0 tee >(sed 's/\x1b\][0-9]*\x07//g;s/\x1b[\[0-9;!?=]*[a-zA-Z]//g;s/\t/    /g;s/[^[:print:]]//g' >>"$log_dir/$log_file_log")
}

run_qemu "🚀  Starting VM..." "${qemu_opts[@]}"

# Check if JUnit log is available and parse results
if [ -f "$log_dir/$log_file_junit" ] && [ "$(wc -c "$log_dir/$log_file_junit" | cut -d' ' -f1)" != "0" ]; then
	command -v xmllint >/dev/null || (
		echo "⚠️  xmllint not found, please install it to parse test results"
		exit 1
	)
	num_errors=$(xmllint --xpath 'string(/testsuites/testsuite/@errors)' "$log_dir/$log_file_junit")
	num_failures=$(xmllint --xpath 'string(/testsuites/testsuite/@failures)' "$log_dir/$log_file_junit")
	if [ "${num_errors}" -gt 0 ] || [ "${num_failures}" -gt 0 ]; then
		exit 1
	fi
else
	if ! ((skip_tests)); then
		echo "⚠️  No test results found in $log_dir/$log_file_junit"
		exit 1
	fi
fi
