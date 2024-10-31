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

	cat > "$initdir/etc/systemd/system/sysroot.mount" <<-EOF
	[Mount]
	What=/root.img
	Where=/sysroot
	Type=erofs
	EOF

	mkdir -p "$initdir/etc/systemd/system/initrd-root-fs.target.requires"
	ln -s "$initdir/etc/systemd/system/sysroot.mount" "$initdir/etc/systemd/system/initrd-root-fs.target.requires/"

	inst /root.img /root.img
	instmods erofs
}
