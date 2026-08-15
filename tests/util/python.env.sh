# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.7"
export RELEASE_DATE="20260814"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="490953e4a7e97a6ed64d0f0bd04f2d4d9a7bb45368890d3fa32ba05d0ff5c48f"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="5bad659dc6d686b430f60104d53abfecb1cd93de37b8aaa112f10f0cea2cb655"
