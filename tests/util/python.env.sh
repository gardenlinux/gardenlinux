# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.7"
export RELEASE_DATE="20260901"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="0ab3305457051cd3e7c031857e005f1bda17c218a1990567dacaaac6dd1d14f0"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="30f1cc489be654477d895b441e196bb080738bf0456da82080ad4ab66a22d80f"
