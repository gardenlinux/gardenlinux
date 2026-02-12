# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.3"
export RELEASE_DATE="20260211"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="a3917eee21b61c9d8bfab22a773d1fe6945683dd40b5d5b263527af2550e3bbf"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="2021bb77a260a53777ba2038759140cfc3ae8abfffec4e6ea769607ec66654eb"
