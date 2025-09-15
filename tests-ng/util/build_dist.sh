#!/usr/bin/env bash

set -eufo pipefail

if [ "$0" != /init ]; then
	exec podman run --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w /mnt debian:stable /init "$@"
fi

tmpdir=

cleanup() {
	[ -z "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

runtime="$1"
output="$2"

mkdir -p "$tmpdir/dist/runtime"
gzip -d <"$runtime" | tar -x -C "$tmpdir/dist/runtime"

set +f

mkdir -p "$tmpdir/dist/tests"
test_dirs=$(find . -mindepth 2 -maxdepth 2 -name "test_*.py" -print0 | xargs -0 -r -I {} dirname {} | sort -u)
cp -r -t "$tmpdir/dist/tests" conftest.py plugins test_*.py
if [ -n "$test_dirs" ]; then
	echo "$test_dirs" | xargs -I {} cp -r {} "$tmpdir/dist/tests/"
fi

mkdir -p "$tmpdir/dist/.vscode"
cat >"$tmpdir/dist/.vscode/extensions.json" <<'EOF'
{
    "recommendations": [
        "ms-python.debugpy"
    ]
}
EOF

cat >"$tmpdir/dist/.vscode/settings.json" <<'EOF'
{
    "python.testing.pytestArgs": [
        "/run/gardenlinux-tests/", "--system-booted", "--expected-users=gardenlinux", "--allow-system-modifications"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
}
EOF

cat >"$tmpdir/dist/run_tests" <<'EOF'
#!/bin/sh

set -e

arch="$(uname -m)"
script_path="$(realpath -- "$0")"
script_dir="$(dirname -- "$script_path")"

export PATH="$script_dir/runtime/$arch/bin:$PATH"
cd "$script_dir/tests"
echo "🧪  running tests with args: $0 $@"
COLUMNS=120 python -m pytest -rA --tb=short --color=yes "$@"
EOF
chmod +x "$tmpdir/dist/run_tests"

tar -c -C "$tmpdir/dist" . | gzip >"$output"
