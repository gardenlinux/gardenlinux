# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.2"
export RELEASE_DATE="20251217"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="5770ce51ee3010cc93951c4f78a84a6d284a129484d040ac23cb762f4005da44"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="dab8067b899e6095a896420a611dbfcf86ec160b9048e11e090d2fe1bcddf2ab"
