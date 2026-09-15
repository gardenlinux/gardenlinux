# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="gardenlinux"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.7"
export RELEASE_DATE="20260901"
export PYTHON_ARCHIVE_SUFFIX="20260901T0901"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="fae180fe6c18354f3078b380a40318c7457910f519299a60d4b3ae98e9bae50e"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="5c617384ef8ad108f80cf29ea7e65d7edc5777ac0c423eeb6b0c5039dc2acb6e"
