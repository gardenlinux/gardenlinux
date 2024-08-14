#!/usr/bin/env sh

type getarg >/dev/null 2>&1 || . /lib/dracut-lib.sh

live=$(getarg gl.live=)
live="${live#gl.live=}"

case "$live" in
	no,false,0,disabled,disable)
            exit 1
            ;;
        *)
            exit 0
            ;;
esac
