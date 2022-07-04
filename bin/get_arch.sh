#!/usr/bin/env bash
set -Eeufo pipefail

case "$(uname -m)" in
	"x86_64"|"amd64")
		echo "amd64"
		;;
	"aarch64"|"arm64")
		echo "arm64"
		;;
	*)
		echo "unsupported architecture" >&2
		exit 1
		;;
esac
