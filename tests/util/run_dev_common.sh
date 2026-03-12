#!/usr/bin/env bash

set -eufo pipefail

watch_mode=false
test_args=""
ssh_private_key="$util_dir/../.ssh/id_ed25519_gl"

while [ $# -gt 0 ]; do
    case "$1" in
    --user)
        ssh_user="$2"
        shift 2
        ;;
    --watch)
        watch_mode=true
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

sync_and_test() {
    echo "🚀  syncing tests to VM"
    cd "$util_dir/.."
    dist_exists=$(
        ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "test -d /run/gardenlinux-tests-dev/runtime; echo \$?"
    )
    # sync dist if it doesn't exist
    if [ "$dist_exists" != "0" ]; then
        ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "sudo rm -rf /run/gardenlinux-tests-dev && sudo mkdir -p /run/gardenlinux-tests-dev && sudo chown -R $ssh_user:$ssh_user /run/gardenlinux-tests-dev"
        gzip -d <.build/dist.tar.gz | ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "tar -C /run/gardenlinux-tests-dev -xf -"
    fi
    # temporarily disable -f for globbing
    set +f
    # sync tests
    tar --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='plugins/tests' \
        -czf - test_*.py conftest.py handlers/ integration/ plugins/ |
        ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "sudo rm -rf /run/gardenlinux-tests-dev/tests && mkdir -p /run/gardenlinux-tests-dev/tests && tar -C /run/gardenlinux-tests-dev/tests -xzf -"
    set -f
    echo "🚀  running tests"
    local test_cmd="cd /run/gardenlinux-tests-dev && sudo ./run_tests --system-booted --allow-system-modifications --expected-users $ssh_user"
    if [ -n "$test_args" ]; then
        test_cmd="$test_cmd $test_args"
    fi
    ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "$test_cmd"
}

if [ "$watch_mode" = true ]; then
    echo "👁️  watching for changes in tests/ and features/ directories..."
    echo "   Press Ctrl+C to exit"
    echo "   Waiting for first change to run tests..."

    inotifywait -m -r -e modify,create,delete,move \
        --exclude '(__pycache__|\.pyc$|\.pytest_cache)' \
        "$util_dir/.." "$util_dir/../../features" 2>/dev/null |
        while read -r directory events filename; do
            echo "🔄  detected change: $filename"
            echo "   waiting 1 second for additional changes..."
            sleep 1
            sync_and_test || true
            echo ""
            echo "👁️  watching for changes..."
        done
else
    sync_and_test
fi
