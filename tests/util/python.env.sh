# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.6"
export RELEASE_DATE="20260610"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="288f0e2c728f2bec803c4bffbd0ad3940190221ef39c1540b69d5e4ad6861b10"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="9bc4a8b40e849c927158403552ffea25627f17776e5200156b131ac78b049384"
