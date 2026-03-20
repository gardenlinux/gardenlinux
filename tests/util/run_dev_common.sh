#!/usr/bin/env bash

set -eufo pipefail

watch=0
test_args=""

while [ $# -gt 0 ]; do
    case "$1" in
    --user)
        ssh_user="$2"
        shift 2
        ;;
    --watch)
        watch=1
        shift
        ;;
    --test-args)
        test_args="$2"
        shift 2
        ;;
    *)
        break
        ;;
    esac
done

# Trap to clean up watch on exit
trap 'kill 0 2>/dev/null || true' EXIT

run_sync() {
    echo "🚀  syncing tests to VM"
    # shellcheck disable=SC2154
    cd "$util_dir/.."
    dist_exists=$(
        # shellcheck disable=SC2154
        ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "test -d /run/gardenlinux-tests-dev/runtime; echo \$?"
    )
    # sync dist if it doesn't exist
    if [ "$dist_exists" != "0" ]; then
        # shellcheck disable=SC2029
        ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "sudo rm -rf /run/gardenlinux-tests-dev && sudo mkdir -p /run/gardenlinux-tests-dev && sudo chown -R $ssh_user:$ssh_user /run/gardenlinux-tests-dev"
        gzip -d <.build/dist.tar.gz | ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "tar -C /run/gardenlinux-tests-dev -xf -"
    fi
    # temporarily disable -f for globbing
    set +f
    # sync tests
    tar --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='plugins/tests' \
        -czf - test_*.py conftest.py handlers/ integration/ plugins/ 2>/dev/null |
        ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "sudo rm -rf /run/gardenlinux-tests-dev/tests && mkdir -p /run/gardenlinux-tests-dev/tests && tar -C /run/gardenlinux-tests-dev/tests -xzf -"
    set -f
}

run_test() {
    echo "🚀  running tests"
    local test_cmd="cd /run/gardenlinux-tests-dev && sudo ./run_tests --system-booted --allow-system-modifications --expected-users $ssh_user"
    if [ -n "$test_args" ]; then
        test_cmd="$test_cmd $test_args"
    fi
    # shellcheck disable=SC2029
    ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "$test_cmd"
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
        "$util_dir/.." "$util_dir/../../features" 2>/dev/null
}

run_watch_macos() {
    command -v fswatch >/dev/null || (echo "Error: fswatch not found. Please install fswatch package." && exit 1)
    fswatch -rEo \
        --event Created --event Updated --event Removed --event Renamed --event MovedFrom --event MovedTo \
        --exclude $EXCLUDE \
        "$util_dir/.." "$util_dir/../../features" 2>/dev/null
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

if ((watch)); then
    run_sync || true
    run_test || true
    run_watch
else
    run_sync || true
    run_test
fi
