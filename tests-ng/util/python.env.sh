# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.2"
export RELEASE_DATE="20260113"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="0ca310e2b1b8e08f3021725c3595d04c2193bdeb81d68372b9240068a128ee59"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="0b3f08d20eaa32f13b46f92b0b333684da3b4c7eb23eb254bdac5afe323bad13"
