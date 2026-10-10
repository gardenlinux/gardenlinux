# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.8"
export RELEASE_DATE="20261009"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="83f9cb480b702548c592443f86209cf0fc03448d90692df257f095c01791dccc"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="2a99838d2ba71c91d9c72929ee73cdfad2ccd093d7746a14094f50e583989ec3"
