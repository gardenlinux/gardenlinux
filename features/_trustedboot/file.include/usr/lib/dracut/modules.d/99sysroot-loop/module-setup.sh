#!/bin/bash

check() {
	return 0
}

depends() {
	echo "systemd"
	return 0
}

install() {
	mkdir -p "$initdir/etc/systemd/system"

	cat > "$initdir/bin/setup-sysroot" <<-EOF
	#!/bin/sh

	set -e

	losetup /dev/loop65535 /root.img
	mount /dev/loop65535 /sysroot
	EOF

	cat > "$initdir/bin/cleanup-sysroot" <<-EOF
	#!/bin/sh

	set -e

	umount -R /sysroot
	losetup -d /dev/loop65535
	EOF

	chmod +x "$initdir/bin/setup-sysroot"
	chmod +x "$initdir/bin/cleanup-sysroot"

	cat > "$initdir/etc/systemd/system/setup-sysroot.service" <<-EOF
	[Unit]
	After=basic.target
	Before=initrd-root-fs.target
	DefaultDependencies=no

	[Service]
	Type=oneshot
	RemainAfterExit=true
	ExecStart=/bin/setup-sysroot
	ExecStop=/bin/cleanup-sysroot
	EOF

	mkdir -p "$initdir/etc/systemd/system/initrd-root-fs.target.requires"
	ln -s "$initdir/etc/systemd/system/setup-sysroot.service" "$initdir/etc/systemd/system/initrd-root-fs.target.requires/"

	inst /root.img /root.img
	instmods erofs
}
