#!/usr/bin/env bash

set -eufo pipefail

test_dist="$1"
arch="$2"
image="$3"

tmpdir=

cleanup () {
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

echo "preparing test VM"

qemu-img create -q -f qcow2 -F raw -b "$(realpath -- "$image")" "$tmpdir/disk.qcow" 4G

mkdir "$tmpdir/test_dist"
gzip -d < "$test_dist" | tar -x -C "$tmpdir/test_dist"
truncate -s 1G "$tmpdir/test_dist.img"
mke2fs -q -t ext2 -d "$tmpdir/test_dist" -L GL_TESTS "$tmpdir/test_dist.img"

curl -sSLf "https://github.com/gardenlinux/edk2-build/releases/download/edk2-stable202505/edk2-qemu-$arch-code" > "$tmpdir/edk2-qemu-code"
curl -sSLf "https://github.com/gardenlinux/edk2-build/releases/download/edk2-stable202505/edk2-qemu-$arch-vars" > "$tmpdir/edk2-qemu-vars"

truncate -s 64M "$tmpdir/edk2-qemu-code"
truncate -s 64M "$tmpdir/edk2-qemu-vars"

cat > "$tmpdir/fw_cfg-script.sh" << 'EOF'
#!/usr/bin/env bash

set -eufo pipefail

trap 'poweroff -f > /dev/null 2>&1' EXIT

mkdir /run/gardenlinux_tests
mount /dev/disk/by-label/GL_TESTS /run/gardenlinux_tests

cd /run/gardenlinux_tests
./run_tests --system-booted > /dev/virtio-ports/test_output
EOF

echo "starting test VM"

if [ "$arch" = x86_64 ]; then
	qemu_machine=q35
	qemu_cpu=qemu64
fi

if [ "$arch" = aarch64 ]; then
	qemu_machine=virt
	qemu_cpu=cortex-a57
fi

if [ -w /dev/kvm ]; then
	qemu_accel=kvm
elif [ "$(uname -s)" = Darwin ]; then
	qemu_accel=hvf
else
	qemu_accel=tcg
fi

qemu_opts=(
	-machine "$qemu_machine"
	-cpu "$qemu_cpu"
	-m 4096
	-accel "$qemu_accel"
	-display none
	-serial stdio
	-drive if=pflash,unit=0,format=raw,file="$tmpdir/edk2-qemu-code,readonly=on"
	-drive if=pflash,unit=1,format=raw,file="$tmpdir/edk2-qemu-vars"
	-drive if=virtio,format=qcow2,file="$tmpdir/disk.qcow"
	-drive if=virtio,format=raw,file="$tmpdir/test_dist.img"
	-fw_cfg name=opt/gardenlinux/config_script,file="$tmpdir/fw_cfg-script.sh"
	-chardev file,id=test_output,path="$tmpdir/serial.log"
	-device virtio-serial
	-device virtserialport,chardev=test_output,name=test_output
)

"qemu-system-$arch" "${qemu_opts[@]}" | stdbuf -i0 -o0 sed 's/\x1b\][0-9]*\x07//g;s/\x1b[\[0-9;!?=]*[a-zA-Z]//g;s/\t/    /g;s/[^[:print:]]//g'
cat "$tmpdir/serial.log"
! ( tail -n1 "$tmpdir/serial.log" | grep failed > /dev/null )
