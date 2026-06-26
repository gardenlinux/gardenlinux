# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.6"
export RELEASE_DATE="20260623"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="3d943d8b4360823959012d7e9f4c755256ac1e9c04b609c24894a1b480736e36"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="93af46aac9d7c210b4842ab2813a2ac6e0af60d2550b3ca5f761f2e0f5e18b64"
