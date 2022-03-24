#!/usr/bin/env bash
set -Eeuo pipefail

# remove any swap partition
sed '/^[^[:space:]]\+[[:space:]]\+[^[:space:]]\+[[:space:]]\+swap[[:space:]]\+/d'

