# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.10"
export RELEASE_DATE="20261026"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="1b38024924eb7f4cf0cab45d7b871d1f1991354190fccd2625ac7529a43786e2"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="dcc31ce7b9ddbbffac160da7fff0cc069054f43eca52382a7d0eebf94e985b88"
