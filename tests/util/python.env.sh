# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.4"
export RELEASE_DATE="20260408"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="ced074da6b6f4d18a8e87199e54bd5d8c2f6ee1dc19edf83f3930c7c6a197a44"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="98a7da87a4c93d2542cee8c41b105648496473dca249c54f7410c5db2d09c232"
