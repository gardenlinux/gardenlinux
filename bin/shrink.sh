#!/bin/bash

set -Eeuo pipefail
set -x

loopback=$(losetup -f --partscan --show rootfs.raw)
trap "losetup -d $loopback 2>/dev/null" EXIT


blocks_fs=0
blocksize=0
sectors_part=0
sectorsize=512
sectors_gpt=34
resizereport=
i=0
while [ -z "$(echo $resizereport | grep "Nothing to do")" ]; do
	let i+=1
	resizereport="$(resize2fs -M ${loopback}p3 2>&1 | grep "^The filesystem")"
	echo "$resizereport"
	[ $i -gt 10 ] && break
done
resizereport=$(echo $resizereport | grep "Nothing to do")

read -r blocks_fs blocksize <<< $(echo "$resizereport" | sed 's/The filesystem is already \([0-9]*\) (\([^)]*\)) blocks long. Nothing to do!/\1 \2/')

if [ ! $blocks_fs -gt 0 ];   then echo "ERROR: cannot determine shrinked size"; exit 1; fi
if [ "$blocksize" != "4k" ]; then echo "ERROR: no standard blocksize 4k!=$blocksize"; exit 1; else blocksize=4096; fi
sectors_part=$(( $blocks_fs*$blocksize/$sectorsize ))
startsector=$(sfdisk $loopback --dump | grep "${loopback}p3" | sed "s+^${loopback}p3 : start= *\(.*\), size=.*, type=.*$+\1+")
sectors_end=$(( $startsector+$sectors_part-1 ))
sectors_final=$(( $sectors_end+$sectors_gpt ))
bytes_end=$(( $sectors_end*$sectorsize ))
bytes_final=$(( $sectors_final*$sectorsize ))

echo "blocks by last FS: $blocks_fs($blocksize) -> Sectors $sectors_part($sectorsize)"
echo "part: start $startsector  end $sectors_end"
echo "finalsize: $bytes_final"

echo ",$sectors_part" | sfdisk -N 3 $loopback --no-reread --no-tell-kernel
sfdisk $loopback --dump > final.sfdisk
losetup -d $loopback
sync

dd if=rootfs.raw of=gpt.bak bs=$sectorsize count=$sectors_gpt seek=$sectors_end

truncate rootfs.raw -s $bytes_end
sync

dd if=gpt.bak of=rootfs.raw bs=$sectorsize count=$sectors_gpt seek=$sectors_end

#loopback=$(losetup -f --partscan --show rootfs.raw)
#echo -e "w\ny" | gdisk $loopback
