# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.3"
export RELEASE_DATE="20260325"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="20d3bcd7f175e09fa08f4cb3039e5f90fe7e4ce2476534e83f5aa21eb0d7cee9"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="112cf42bdf4d04f69ff4f9bf18c8ce45f494bac1645310bfdeff6f2ffb30dd9a"
