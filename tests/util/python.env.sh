# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.9"
export RELEASE_DATE="20261021"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="dfa4c5a40c47f338f41658017be550c72247c391e6bfb1fa4da03ebc8451abdf"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="847895ba727440b012207bb0192282d7e182eb991ae5c7bb5c35c6a12a99e732"
