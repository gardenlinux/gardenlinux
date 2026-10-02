# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.8"
export RELEASE_DATE="20261001"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="813c89e2589fed92333e18bde230a43280962e6f24bb0b861dc8ce532cfd6567"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="1e59925c73df6f8233355f394023b02bb87a768243e6727b449c741a4c8133d3"
