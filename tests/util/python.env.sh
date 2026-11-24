# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.10"
export RELEASE_DATE="20261123"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="6f216be7b5209a88586d5b6cf84ffd953db83d8942c5eb3b09517d056dac0d8d"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="e22a598b87c744318e3c0da365f2d2f1880ff4b46c851fb5ec0fcd20a9397ef8"
