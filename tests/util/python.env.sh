# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.6"
export RELEASE_DATE="20260718"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="b442fb93903c6f3392b2430961d4725354ae0da7558c785a908d714264309b28"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="97f9ddaa547f9420a5ab59e9eac7a5b04acd96acec2ef532f4a64283e3164aad"
