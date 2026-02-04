# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.2"
export RELEASE_DATE="20260127"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="bfb704b307ad69f30d36e936026504ab3ad29883c572362d4f32f2d1005abde3"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="bd5cc84e921615cef52e4c11baa01748176a141e22506f15932d910699ec99b1"
