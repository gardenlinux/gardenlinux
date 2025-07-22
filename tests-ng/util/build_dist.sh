#!/usr/bin/env bash

set -eufo pipefail

if [ "$0" != /init ]; then
	exec podman run --rm -v "$(realpath -- "${BASH_SOURCE[0]}"):/init:ro" -v "$PWD:/mnt" -w /mnt debian:stable /init "$@"
fi

tmpdir=

cleanup() {
	[ -n "$tmpdir" ] || rm -rf "$tmpdir"
	tmpdir=
}

trap cleanup EXIT
tmpdir="$(mktemp -d)"

output="$1"
shift
runtimes=("$@")

mkdir -p "$tmpdir/dist/runtime"
for runtime in "${runtimes[@]}"; do
	IFS=: read runtime_arch runtime_tar <<<"$runtime"
	mkdir "$tmpdir/dist/runtime/$runtime_arch"
	gzip -d <"$runtime_tar" | tar -x -C "$tmpdir/dist/runtime/$runtime_arch"
	# NOTE: as for now, we should not depend on any binary packages
	# therefore, we only need to keep the site-packages directory in the root of the runtime
	# and symlink it to the other architectures
	PYTHON_LIB_DIR="$(find $tmpdir/dist/runtime/$runtime_arch/lib -type d -name python*)"
	if [ "$runtime_arch" = "x86_64" ]; then
		mv "$PYTHON_LIB_DIR/site-packages" "$tmpdir/dist/runtime/site-packages"
	else
		rm -rf "$PYTHON_LIB_DIR/site-packages"
	fi
	(cd "$PYTHON_LIB_DIR" && ln -s ../../site-packages)
done

set +f

mkdir -p "$tmpdir/dist/tests"
cp -r -t "$tmpdir/dist/tests" conftest.py plugins test_*.py

cat >"$tmpdir/dist/run_tests" <<'EOF'
#!/bin/sh

set -e

arch="$(uname -m)"
script_path="$(realpath -- "$0")"
script_dir="$(dirname -- "$script_path")"

export PATH="$script_dir/runtime/$arch/bin:$PATH"
cd "$script_dir/tests"
COLUMNS=120 python -m pytest -rA --tb=short --color=yes "$@"
EOF
chmod +x "$tmpdir/dist/run_tests"

tar -c -C "$tmpdir/dist" . | gzip >"$output"
