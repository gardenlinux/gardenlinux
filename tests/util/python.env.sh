# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.7"
export RELEASE_DATE="20260924"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="5539eaf1de20bd9b5f43ea11c3c1f84cbac74fe927ac050318a9210c022618cb"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="0dec153b4932cfa7094d4b6772022a503c7842a6c07978576695f8b5a8785055"
