#!/bin/bash

set -Eeuo pipefail
set -x

loopback=$(losetup -f --partscan --show rootfs.raw)
trap "losetup -d $loopback 2>/dev/null" EXIT


blocks=0
blocksize=0
sectorsize=512
gptbackup=2048
resizereport=
i=0
while [ -z "$(echo $resizereport | grep "Nothing to do")" ]; do
	let i+=1
	resizereport="$(resize2fs -M ${loopback}p3 2>&1 | grep "^The filesystem")"
	echo "$resizereport"
	[ $i -gt 10 ] && break
done
resizereport=$(echo $resizereport | grep "Nothing to do")

read -r blocks blocksize <<< $(echo "$resizereport" | sed 's/The filesystem is already \([0-9]*\) (\([^)]*\)) blocks long. Nothing to do!/\1 \2/')

if [ ! $blocks -gt 0 ];      then echo "ERROR: cannot determine shrinked size"; exit 1; fi
if [ "$blocksize" != "4k" ]; then echo "ERROR: no standard blocksize 4k!=$blocksize"; exit 1; else blocksize=4096; fi
sizepart=$(( $blocks*$blocksize/$sectorsize ))
startpart=$(sfdisk $loopback --dump | grep "${loopback}p3" | sed "s+^${loopback}p3 : start= *\(.*\), size=.*, type=.*$+\1+")
finalsize=$(( ($startpart+$sizepart-1+$gptbackup)*$sectorsize ))

sfdisk $loopback --dump
echo "blocks by last FS: $blocks($blocksize) -> Sectors $sizepart($sectorsize)"
echo "startpart: $startpart"
echo "finalsize: $finalsize"

echo ",$sizepart" | sfdisk -N 3 $loopback --no-reread --no-tell-kernel
losetup -d $loopback
sync

truncate rootfs.raw -s $finalsize
sync

loopback=$(losetup -f --partscan --show rootfs.raw)
echo -e "w\ny" | gdisk /dev/loop0
