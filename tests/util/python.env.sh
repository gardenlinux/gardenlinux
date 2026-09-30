# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.7"
export RELEASE_DATE="20260929"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="0056208b5fdfcec939bc5b3908f5e7c89d11c6e2f1fdf02c9cc6aa98d10c5d05"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="08a224bc0bcadfee3eab55db618343e6ba221f3595000e0894aae163648abc9d"
