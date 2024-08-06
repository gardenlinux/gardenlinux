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

	cat > "$initdir/bin/setup-etc-overlay" <<-EOF
	#!/bin/sh

	set -e

	mount -t tmpfs -o mode=0755 none /sysroot/overlay
	mkdir /sysroot/overlay/upperdir /sysroot/overlay/workdir
	mount -t overlay -o lowerdir=/sysroot/etc,upperdir=/sysroot/overlay/upperdir,workdir=/sysroot/overlay/workdir overlay /sysroot/etc
	EOF

	chmod +x "$initdir/bin/setup-etc-overlay"

	cat > "$initdir/etc/systemd/system/setup-etc-overlay.service" <<-EOF
	[Unit]
	Requires=initrd-root-fs.target
	After=initrd-root-fs.target
	Before=initrd-fs.target
	DefaultDependencies=no

	[Service]
	Type=oneshot
	RemainAfterExit=true
	ExecStart=/bin/setup-etc-overlay
	EOF

	mkdir -p "$initdir/etc/systemd/system/initrd-fs.target.requires"
	ln -s "$initdir/etc/systemd/system/setup-etc-overlay.service" "$initdir/etc/systemd/system/initrd-fs.target.requires/"
}
