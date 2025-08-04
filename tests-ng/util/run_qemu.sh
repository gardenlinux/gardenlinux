#!/usr/bin/env bash

set -eufo pipefail

map_arch () {
	local arg="$1"
	if [ "$arg" = amd64 ]; then
		arg=x86_64
	elif [ "$arg" = arm64 ]; then
		arg=aarch64
	fi
	echo "$arg"
}

arch=

while [ $# -gt 0 ]; do
	case "$1" in
		--arch)
			arch="$(map_arch "$2")"
			shift 2
			;;
		*)
			break
			;;
	esac
done

[ -n "$arch" ]

test_dist_dir="$1"
image="$2"

tmpdir=

cleanup () {
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

echo "⚙️  preparing test VM"

qemu-img create -q -f qcow2 -F raw -b "$(realpath -- "$image")" "$tmpdir/disk.qcow" 4G

cp "$test_dist_dir/edk2-qemu-$arch-code" "$tmpdir/edk2-qemu-code"
cp "$test_dist_dir/edk2-qemu-$arch-vars" "$tmpdir/edk2-qemu-vars"

if [ "$arch" = aarch64 ]; then
	truncate -s 64M "$tmpdir/edk2-qemu-code"
	truncate -s 64M "$tmpdir/edk2-qemu-vars"
fi

cat > "$tmpdir/fw_cfg-script.sh" << 'EOF'
#!/usr/bin/env bash

set -eufo pipefail

exec 1>/dev/virtio-ports/test_output
exec 2>&1

trap 'poweroff -f > /dev/null 2>&1' EXIT

mkdir /run/gardenlinux_tests
mount -o ro /dev/disk/by-label/GL_TESTS /run/gardenlinux_tests

cd /run/gardenlinux_tests
EOF

echo "🚀  starting test VM"

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
		qemu_accel=hvf
	fi
fi

if [ "$qemu_accel" != tcg ]; then
	echo './run_tests --system-booted' >> "$tmpdir/fw_cfg-script.sh"
else
	echo './run_tests --system-booted --skip-performance-metrics' >> "$tmpdir/fw_cfg-script.sh"
fi

qemu_opts=(
	-machine "$qemu_machine"
	-cpu "$qemu_cpu"
	-m 4096
	-accel "$qemu_accel"
	-display none
	-serial stdio
	-drive if=pflash,unit=0,format=raw,readonly=on,file="$tmpdir/edk2-qemu-code"
	-drive if=pflash,unit=1,format=raw,file="$tmpdir/edk2-qemu-vars"
	-drive if=virtio,format=qcow2,file="$tmpdir/disk.qcow"
	-drive if=virtio,format=raw,readonly=on,file="$test_dist_dir/dist.ext2"
	-fw_cfg name=opt/gardenlinux/config_script,file="$tmpdir/fw_cfg-script.sh"
	-chardev file,id=test_output,path="$tmpdir/serial.log"
	-device virtio-serial
	-device virtserialport,chardev=test_output,name=test_output
	-chardev socket,id=chrtpm,path="$tmpdir/swtpm.sock"
	-tpmdev emulator,id=tpm0,chardev=chrtpm
	-device "$qemu_tpm_dev",tpmdev=tpm0
)

swtpm socket --tpmstate backend-uri="file://$tmpdir/swtpm.permall" --ctrl type=unixio,path="$tmpdir/swtpm.sock" --tpm2 --daemon --terminate
"qemu-system-$arch" "${qemu_opts[@]}" | stdbuf -i0 -o0 sed 's/\x1b\][0-9]*\x07//g;s/\x1b[\[0-9;!?=]*[a-zA-Z]//g;s/\t/    /g;s/[^[:print:]]//g'
cat "$tmpdir/serial.log"
! ( tail -n1 "$tmpdir/serial.log" | grep failed > /dev/null )
