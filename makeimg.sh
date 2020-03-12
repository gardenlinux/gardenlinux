#!/bin/sh

docker build -f Dockerfile.guestfs . -t guestfs

dd if=/dev/zero of=$1.raw seek=2048 bs=1 count=0 seek=2G

docker run --rm -it --privileged -v $1.raw:/$1.raw guestfs guestfish -i -a /$1.raw

exit 1

guestfish << EOF
disk-create test.img raw 2G preallocation:sparse
add test.img format:raw name:/dev/sda cachemode:unsafe discard:enable
run
part-init /dev/sda gpt
part-add /dev/sda p 2048 2096127
part-add /dev/sda p 2096128 4194270
part-set-gpt-type /dev/sda 1 C12A7328-F81F-11D2-BA4B-00A0C93EC93B
part-set-gpt-type /dev/sda 2 0FC63DAF-8483-4772-8E79-3D69D8477DE4
mkfs vfat /dev/sda1 label:EFI
mke2fs /dev/sda2 label:ROOT fstype:ext4
mount /dev/sda2 /
mkdir /boot
mount /dev/sda1 /boot
tar-in $target.tar /
EOF


