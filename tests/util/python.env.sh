# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.5"
export RELEASE_DATE="20260510"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="b3916b829fb0bc9efe93e800e6738a629ee4ade4aad798378d9326f4a0bac2db"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="aa63daf3aff8360baf6888c24fb5dde155f0895f3d83eb9ddf172ba5c6c17c33"
