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
export PYTHON_ARCHIVE_CHECKSUM_AMD64="c1a845a79da56265dc49628bc3b9e20d34f04674fd2d637ee40cbe259d2b1b95"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="6d84fb153ccb5cb650652aadc490d99881a8d9b68cf273d44cb553e8cd087734"
