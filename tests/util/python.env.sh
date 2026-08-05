# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.6"
export RELEASE_DATE="20260804"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="8fa4614f8c2d47430d5573098fad787c44bb314830fd2e826952335446706e45"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="30653ace38356262c0bd885219fe2d8ca1702303d1ed2facb070a1e4a0d6c617"
