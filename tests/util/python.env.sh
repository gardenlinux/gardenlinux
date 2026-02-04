# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.3"
export RELEASE_DATE="20260203"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="d4c6712210b69540ab4ed51825b99388b200e4f90ca4e53fbb5a67c2467feb48"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="f6528fc435468bd0212003bc3d4db0fabb995ceec7dc0fba3450744834be569a"
