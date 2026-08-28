# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.7"
export RELEASE_DATE="20260805"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="64ebb7e4ef74b03e8038ba07209ab1fce62fcbe4afafbbce5a27216fbffde5ff"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="90e4d9b59c587651f9eb081d79b0bb899e5c1705acf4fb537f4eb674b5309135"
