# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.10"
export RELEASE_DATE="20261124"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="bfa2f9fe1691f14a98c37e206641058ad7116db117ac924fdcab744987107ad8"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="4a5d38d83b7cab3b1ee53b9fe398ba5bf43d737acca4f7bc06b9deb6ac0e7405"
