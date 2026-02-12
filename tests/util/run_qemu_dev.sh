#!/usr/bin/env bash

set -eufo pipefail

ssh_user=gardenlinux
watch_mode=false
test_args=""
util_dir="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")")"
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

vm_ip="127.0.0.1"
ssh_opts=(-p 2222 -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i "$ssh_private_key")
scp_opts=(-P 2222 -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i "$ssh_private_key")

sync_and_test() {
    echo "🚀  syncing tests to VM"
    ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "sudo rm -rf /run/gardenlinux-tests-dev && sudo mkdir -p /run/gardenlinux-tests-dev && sudo cp -r /run/gardenlinux-tests/{run_tests,runtime} /run/gardenlinux-tests-dev && sudo mkdir -p /run/gardenlinux-tests-dev/tests && sudo chown -R $ssh_user:$ssh_user /run/gardenlinux-tests-dev"
    cd "$util_dir/.."
    # temporarily disable -f for globbing
    set +f
    tar --exclude='*.pyc' \
        --exclude='__pycache__' \
        -czf - test_*.py conftest.py plugins/ handlers/ |
        ssh "${ssh_opts[@]}" "$ssh_user@$vm_ip" "tar -C /run/gardenlinux-tests-dev/tests -xzf -"
    set -f
    echo "🚀  running tests"
    local test_cmd="cd /run/gardenlinux-tests-dev && ./run_tests --system-booted --allow-system-modifications --expected-users gardenlinux"
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
