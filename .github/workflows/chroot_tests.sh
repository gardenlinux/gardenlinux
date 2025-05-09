#!/bin/bash
#set -Eeuo pipefail

cname="${@: -1}"
./test "${cname}"
