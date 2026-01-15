# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.2"
export RELEASE_DATE="20260114"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="fae1c3b125cbc4b71919154330bf2c995ce9e0e75cbbb98439dcb2746d34e719"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="e38e296cd6cb522645b8efdd34a908be9d6e252a5ac0b537065772a822e8bd67"
