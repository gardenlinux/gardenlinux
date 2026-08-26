# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.7"
export RELEASE_DATE="20260825"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="d68dfa9c5d37afec0a4c8ffbf5c20d05d34492bd4561c94d7c3c7578e21a7f71"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="bd5e9541a62fd1143270a38c2c1cdb94c7a1015c6d104aefa9e12ab5f80370b2"
