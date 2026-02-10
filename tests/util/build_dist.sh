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
cp -r -t "$tmpdir/dist/tests" conftest.py handlers integration plugins

# We need the OPENSSL_MODULES=/usr/lib/$(arch)-linux-gnu/ossl-modules/ to allow the python-build-standalone
# to detect the fips.so module. See https://github.com/gardenlinux/gardenlinux/pull/3752
cat >"$tmpdir/dist/run_tests" <<'EOF'
#!/bin/sh

set -e

arch="$(uname -m)"
script_path="$(realpath -- "$0")"
script_dir="$(dirname -- "$script_path")"

export PATH="$script_dir/runtime/$arch/bin:$PATH"
cd "$script_dir/tests"
echo "🧪  running tests with args: $0 $@"
error=0
COLUMNS=120 OPENSSL_MODULES=/usr/lib/$(arch)-linux-gnu/ossl-modules/ python -m pytest -rA --tb=short --color=yes -p no:cacheprovider "$@" || error=$?
if [ "$TEST_NG_EXIT_0" = 1 ]; then
	error=0
fi
exit "$error"
EOF
chmod +x "$tmpdir/dist/run_tests"

tar -c -C "$tmpdir/dist" . | gzip >"$output"
