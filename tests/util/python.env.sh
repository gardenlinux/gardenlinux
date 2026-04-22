# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.4"
export RELEASE_DATE="20260414"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="e17275eaf95ceb5877aa6816e209b7733f41fee401d39c3921b88fb73fc4a4ba"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="5c8db1c21023316adad827a46d917bbbd6a85ae4e39bc3a58febda712c2f963d"
