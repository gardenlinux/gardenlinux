#!/usr/bin/env bash

set -eufo pipefail

containerize=0

if [ "$(uname -s)" != Linux ]; then
	containerize=1
fi

while [ $# -gt 0 ]; do
	case "$1" in
		--containerize) containerize=1; shift ;;
		--no-containerize) containerize=0; shift ;;
		*) break ;;
	esac
done

test_dist_dir="$1"
rootfs_tar="$2"

if (( containerize )); then
	dir="$(realpath "$(dirname "${BASH_SOURCE[0]}")"/../..)"
	container_image="$("$dir/build" --print-container-image)"
	exec podman run --rm \
		-v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" \
		-v "$(realpath -- "$test_dist_dir/dist.tar.gz"):/mnt/test_dist/dist.tar.gz:ro" \
		-v "$(realpath -- "$rootfs_tar"):/mnt/rootfs.tar:ro" \
		"$container_image" fake_xattr /init --no-containerize /mnt/test_dist /mnt/rootfs.tar
fi

tmpdir=

cleanup () {
	[ -z "$tmpdir" ] || [ ! -e "$tmpdir/chroot" ] || umount -l "$tmpdir/chroot" || rmdir "$tmpdir/chroot"
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

echo "⚙️  creating chroot for test run"

mkdir "$tmpdir/chroot"
mount -t tmpfs -o mode=0755 none "$tmpdir/chroot"

tar --extract --xattrs --xattrs-include 'security.*' --directory "$tmpdir/chroot" < "$rootfs_tar"

mount --rbind --make-rprivate /proc "$tmpdir/chroot/proc"
mount --rbind --make-rprivate /sys "$tmpdir/chroot/sys"
mount --rbind --make-rprivate /dev "$tmpdir/chroot/dev"

echo "⚙️  setting up test framework"

mkdir "$tmpdir/chroot/run/gardenlinux_tests"
gzip -d < "$test_dist_dir/dist.tar.gz" | tar --extract --directory "$tmpdir/chroot/run/gardenlinux_tests"

env -i /sbin/chroot "$tmpdir/chroot" /bin/sh -c 'cd /run/gardenlinux_tests && ./run_tests'
