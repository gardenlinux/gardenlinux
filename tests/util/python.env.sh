# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.6"
export RELEASE_DATE="20260728"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="b1ff3bb3ca58e2af9f1cb2be63cd9ef00a6f60ed50bba77bab189a9a3df13675"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="1001d13aaccbb3d1a855ec450e0f058f6501259011b74d5b1d086441b21c0dbe"
