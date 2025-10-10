#!/usr/bin/env bash

set -eufo pipefail

containerize=0
test_args=()

if [ "$(uname -s)" != Linux ]; then
	containerize=1
elif [ "$(id -u)" != 0 ]; then
	containerize=1
fi

while [ $# -gt 0 ]; do
	case "$1" in
	--containerize)
		containerize=1
		shift
		;;
	--no-containerize)
		containerize=0
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
rootfs_tar="$2"
log_dir="$test_dist_dir/../log"
log_file_log="chroot.test-ng.log"
log_file_junit="chroot.test-ng.xml"

mkdir -p "$log_dir"
test_args+=("--junit-xml=$log_dir/$log_file_junit")

if ((containerize)); then
	log_dir="/mnt/log"
	dir="$(realpath "$(dirname "${BASH_SOURCE[0]}")"/../..)"
	container_image="$("$dir/build" --print-container-image)"

	test_args_str="${test_args[*]}"

	exec podman run -q --rm \
		-v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" \
		-v "$(realpath -- "$test_dist_dir/dist.tar.gz"):/mnt/test_dist/dist.tar.gz:ro" \
		-v "$(realpath -- "$rootfs_tar"):/mnt/rootfs.tar:ro" \
		-v "$(realpath -- "$test_dist_dir/../log"):$log_dir:rw" \
		"$container_image" fake_xattr /init --no-containerize --test-args "$test_args_str" /mnt/test_dist /mnt/rootfs.tar
fi

tmpdir=

cleanup() {
	get_logs
	[ -z "$tmpdir" ] || [ ! -e "$tmpdir/chroot" ] || umount -l "$tmpdir/chroot" || rmdir "$tmpdir/chroot"
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

get_logs() {
	cp "$tmpdir/chroot/mnt/log/$log_file_junit" "$log_dir" || true
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

echo "⚙️  creating chroot for test run"

mkdir "$tmpdir/chroot"
mount -t tmpfs -o mode=0755 none "$tmpdir/chroot"

tar --extract --xattrs --xattrs-include 'security.*' --directory "$tmpdir/chroot" <"$rootfs_tar"

mount --rbind --make-rprivate /proc "$tmpdir/chroot/proc"
mount --rbind --make-rprivate /sys "$tmpdir/chroot/sys"
mount --rbind --make-rprivate /dev "$tmpdir/chroot/dev"

echo "⚙️  setting up test framework"

mkdir "$tmpdir/chroot/run/gardenlinux-tests"
gzip -d <"$test_dist_dir/dist.tar.gz" | tar --extract --directory "$tmpdir/chroot/run/gardenlinux-tests"

test_args+=("--allow-system-modifications")

env -i /sbin/chroot "$tmpdir/chroot" /bin/sh -c "cd /run/gardenlinux-tests && ./run_tests ${test_args[*]@Q} 2>&1" |
	tee "$log_dir/$log_file_log"
