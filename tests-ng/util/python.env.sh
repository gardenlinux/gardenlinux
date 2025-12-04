# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.1"
export RELEASE_DATE="20251202"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="a72f313bad49846e5e9671af2be7476033a877c80831cf47f431400ccb520090"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="5dde7dba0b8ef34c0d5cb8a721254b1e11028bfc09ff06664879c245fe8df73f"
