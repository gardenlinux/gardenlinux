# python.env.sh
# shellcheck shell=bash
# This file is sourced to populate environment variables
# It is updated by .github/workflows/test_update_python_runtime.yml


export PYTHON_REPO_OWNER="astral-sh"
export PYTHON_REPO_NAME="python-build-standalone"
export PYTHON_SOURCE="https://github.com/${PYTHON_REPO_OWNER}/${PYTHON_REPO_NAME}/releases/download"
export PYTHON_VERSION_SHORT="3.14"
export PYTHON_VERSION="3.14.7"
export RELEASE_DATE="20260807"
export PYTHON_ARCHIVE_CHECKSUM_AMD64="3d1705fee7747c491d774e26fa91fad67e25d1eb3ede4124dc88501279f2e7d4"
export PYTHON_ARCHIVE_CHECKSUM_ARM64="3657f14592d0a9c3f459ded52bf6f38976698cb07365e4025684bb11dd6be1cb"
