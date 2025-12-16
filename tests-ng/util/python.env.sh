# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.2"
export RELEASE_DATE="20251209"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="121c3249bef497adf601df76a4d89aed6053fc5ec2f8c0ec656b86f0142e8ddd"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="869af31b2963194e8a2ecfadc36027c4c1c86a10f4960baec36dadb41b2acf02"
