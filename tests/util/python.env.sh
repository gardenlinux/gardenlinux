# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.10"
export RELEASE_DATE="20261110"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="3fe0d7c0538eb5d190c34582992d26230532551355cbd789fabc6591621cfc07"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="e59f83159984a55e719bb3805a0b2b5b281f645769222218084b78b92eedc07f"
