# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.8"
export RELEASE_DATE="20261003"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="371b6c281bbb09b29279e9e3a2996bab4ae2ea03cca52bf869f8bd89286b0ae8"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="abc0c8dd54a144909a5e4905737bc33f244cb17ce8afc4a7b0791ee1e006ae23"
