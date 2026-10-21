# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.8"
export RELEASE_DATE="20261020"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="1a7081142f62b54d55b7f307e85b86bf7e5a2e4dca8d6424cc5dd928d9cdc34f"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="5fcc838dbffe023945e495904c5d84a71065f564bf720d84eebae59f0bf72997"
