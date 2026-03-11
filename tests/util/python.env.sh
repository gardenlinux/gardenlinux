# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.3"
export RELEASE_DATE="20260310"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="26009c96926828784c81e36727f4af950c9c4bc9368dc744280a6345c38e95e8"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="ccd5bf48febc50732e528f053535c78cf27e02436d8df508f8fec65abcd72100"
