#!/usr/bin/env bash

set -eufo pipefail

containerize=0
watch=0
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
	--watch)
		watch=1
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
log_file_log="chroot.test.log"
log_file_junit="chroot.test.xml"

get_logs() {
	echo cp "$tmpdir/chroot/run/gardenlinux-tests/tests/log/$log_file_junit" "$log_dir" || true
}

run_sync() {
	mkdir -p "$tmpdir/chroot"
	mount -t tmpfs -o mode=0755 none "$tmpdir/chroot"

	tar --extract --xattrs --xattrs-include 'security.*' --directory "$tmpdir/chroot" <"$rootfs_tar"

	mount --rbind --make-rprivate /proc "$tmpdir/chroot/proc"
	mount --rbind --make-rprivate /sys "$tmpdir/chroot/sys"
	mount --rbind --make-rprivate /dev "$tmpdir/chroot/dev"

	echo "⚙️  setting up test framework"

	mkdir "$tmpdir/chroot/run/gardenlinux-tests"
	gzip -d <"$test_dist_dir/dist.tar.gz" | tar --extract --directory "$tmpdir/chroot/run/gardenlinux-tests"
}

run_test() {
	env -i /sbin/chroot "$tmpdir/chroot" /bin/sh -c "cd /run/gardenlinux-tests && ./run_tests ${test_args[*]@Q} 2>&1" |
		tee "$log_dir/$log_file_log"
}

print_watch() {
	echo "👁️  watching for changes in tests/ and features/ directories..."
	echo "   Press Ctrl+C to exit"
}

EXCLUDE='(__pycache__|\.pyc$|\.pytest_cache|\.test\.log|\.test\.xml|~|\.swp$|\.swo$)'

run_watch_linux() {
	command -v inotifywait >/dev/null || (echo "Error: inotifywait not found. Please install inotify-tools package." && exit 1)
	inotifywait -m -r -e modify,create,delete,move \
		--exclude $EXCLUDE \
		"/mnt/watch/tests" "/mnt/watch/features" 2>/dev/null
}

run_watch_macos() {
	command -v fswatch >/dev/null || (echo "Error: fswatch not found. Please install fswatch package." && exit 1)
	fswatch -rEo \
		--event Created --event Updated --event Removed --event Renamed --event MovedFrom --event MovedTo \
		--exclude $EXCLUDE \
		"/mnt/watch/tests" "/mnt/watch/features" 2>/dev/null
}

run_watch_read() {
	while read -r _num1; do
		echo "🔄  detected change"
		# Drain all remaining events
		while read -t 0.5 -r _num2; do
			:
		done
		run_sync || true
		run_test || true
		print_watch
	done
}

run_watch() {
	print_watch
	# Run watch in the background so we can track its PID
	if [[ "$OSTYPE" == "linux-gnu"* ]]; then
		run_watch_linux | run_watch_read &
	else
		run_watch_macos | run_watch_read &
	fi
	watch_pid=$!
	wait "$watch_pid"
}

container_name="gl-chroot-test-$$"
tmpdir=

cleanup() {
	podman rm -f "$container_name" 2>/dev/null || true

	get_logs
	[ -z "$tmpdir" ] || [ ! -e "$tmpdir/chroot" ] || umount -l "$tmpdir/chroot" || rmdir "$tmpdir/chroot"
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}
trap cleanup EXIT INT TERM

mkdir -p "$log_dir"
tmpdir="$(mktemp -d)"

tmpdir=

cleanup() {
	get_logs
	[ -z "$tmpdir" ] || [ ! -e "$tmpdir/chroot" ] || umount -l "$tmpdir/chroot" || rmdir "$tmpdir/chroot"
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}
trap cleanup EXIT
tmpdir="$(mktemp -d)"

get_logs() {
	cp "$tmpdir/chroot/run/gardenlinux-tests/tests/log/$log_file_junit" "$log_dir" || true
}

run_sync() {
	mkdir -p "$tmpdir/chroot"
	mount -t tmpfs -o mode=0755 none "$tmpdir/chroot"

	tar --extract --xattrs --xattrs-include 'security.*' --directory "$tmpdir/chroot" <"$rootfs_tar"

	mount --rbind --make-rprivate /proc "$tmpdir/chroot/proc"
	mount --rbind --make-rprivate /sys "$tmpdir/chroot/sys"
	mount --rbind --make-rprivate /dev "$tmpdir/chroot/dev"

	echo "⚙️  setting up test framework"

	mkdir "$tmpdir/chroot/run/gardenlinux-tests"
	gzip -d <"$test_dist_dir/dist.tar.gz" | tar --extract --directory "$tmpdir/chroot/run/gardenlinux-tests"
}

run_test() {
	env -i /sbin/chroot "$tmpdir/chroot" /bin/sh -c "cd /run/gardenlinux-tests && ./run_tests ${test_args[*]@Q} 2>&1" |
		tee "$log_dir/$log_file_log"
}

print_watch() {
	echo "👁️  watching for changes in tests/ and features/ directories..."
	echo "   Press Ctrl+C to exit"
}

EXCLUDE='(__pycache__|\.pyc$|\.pytest_cache|\.test\.log|\.test\.xml|~|\.swp$|\.swo$)'

run_watch_linux() {
	command -v inotifywait >/dev/null || (echo "Error: inotifywait not found. Please install inotify-tools package." && exit 1)
	inotifywait -m -r -e modify,create,delete,move \
		--exclude $EXCLUDE \
		"/mnt/watch/tests" "/mnt/watch/features" 2>/dev/null
}

run_watch_macos() {
	command -v fswatch >/dev/null || (echo "Error: fswatch not found. Please install fswatch package." && exit 1)
	fswatch -rEo \
		--event Created --event Updated --event Removed --event Renamed --event MovedFrom --event MovedTo \
		--exclude $EXCLUDE \
		"/mnt/watch/tests" "/mnt/watch/features" 2>/dev/null
}

run_watch_read() {
	while read -r _num1; do
		echo "🔄  detected change"
		# Drain all remaining events
		while read -t 0.5 -r _num2; do
			:
		done
		run_sync || true
		run_test || true
		print_watch
	done
}

run_watch() {
	print_watch
	# Run watch in the background so we can track its PID
	if [[ "$OSTYPE" == "linux-gnu"* ]]; then
		run_watch_linux | run_watch_read &
	else
		run_watch_macos | run_watch_read &
	fi
	watch_pid=$!
	wait "$watch_pid"
}

container_name="gl-chroot-test-$$"

cleanup_container() {
	podman rm -f "$container_name" 2>/dev/null || true
}
trap cleanup_container EXIT INT TERM

if [[ "$rootfs_tar" != "/mnt/rootfs.tar" ]]; then
	# We're not running inside a container, extract artifact name and add metadata
	test_artifact="$(basename "$rootfs_tar" | sed 's/-[0-9].*\.tar$//')"
	test_type="chroot"
	test_namespace="test"

	echo "📊  metadata: Artifact=$test_artifact, Type=$test_type, Namespace=$test_namespace"

	test_args+=("--metadata" "Artifact" "$test_artifact")
	test_args+=("--metadata" "Type" "$test_type")
	test_args+=("--metadata" "Namespace" "$test_namespace")

	test_args+=("--junit-xml=$log_dir/$log_file_junit")
fi

if ((containerize)); then
	log_dir="/mnt/log"
	dir="$(realpath "$(dirname "${BASH_SOURCE[0]}")"/../..)"
	container_image="$("$dir/build" --print-container-image)"

	cat >"$tmpdir/Containerfile" <<-EOF
		FROM $container_image
		RUN apt-get update \
		  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends inotify-tools
	EOF

	podman build -q --iidfile "$tmpdir/image_id" "$tmpdir" >/dev/null
	image_id="$(<"$tmpdir/image_id")"

	container_cmd=(/init --no-containerize)
	if ((watch)); then
		container_cmd+=(--watch)
	fi
	if [ ${#test_args[@]} -gt 0 ]; then
		container_cmd+=(--test-args "${test_args[*]}")
	fi
	container_cmd+=(/mnt/test_dist /mnt/rootfs.tar)

	podman run -q --rm --name "$container_name" --stop-signal=SIGINT \
		-v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" \
		-v "$(realpath -- "$test_dist_dir/dist.tar.gz"):/mnt/test_dist/dist.tar.gz:ro" \
		-v "$(realpath -- "$rootfs_tar"):/mnt/rootfs.tar:ro" \
		-v "$(realpath -- "$test_dist_dir/../log"):$log_dir:rw" \
		-v "$(realpath -- "$test_dist_dir/../.."):/mnt/watch:ro" \
		"$image_id" fake_xattr "${container_cmd[@]}" &

	podman_pid=$!
	wait "$podman_pid" 2>/dev/null || true

	# Exit to prevent falling through to non-containerized code path
	exit 0
fi
echo "⚙️  creating chroot for test run"

test_args+=("--allow-system-modifications")

command -v inotifywait >/dev/null || (echo "Error: inotifywait not found. Please install inotify-tools package." && exit 1)

if ((watch)); then
	run_sync
	run_test || true
	run_watch
else
	run_sync
	run_test
fi
