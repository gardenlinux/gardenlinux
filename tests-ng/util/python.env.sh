# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.2"
export RELEASE_DATE="20251205"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="a8b814b182cf21a377665b70c87f9fe56e12add84c4fe338139d6a888740dadd"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="b1f3ed90b90af5493d2922b634b67e66446cf7d6de3327944aaa8a2b49e4b7cc"
