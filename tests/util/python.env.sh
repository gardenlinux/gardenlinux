# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.8"
export RELEASE_DATE="20261013"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="322271a761140ffb3f522431048f701831e412c8f64770103d2b881ee2bbaed0"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="6c3cfb175acca2748d5a9e42208c523bfbc1099ddb928615b5f328ba7c106e83"
