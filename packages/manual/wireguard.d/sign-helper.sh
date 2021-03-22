#!/bin/sh

echo "signing $2"
/usr/lib/linux-kbuild-5.4/scripts/sign-file sha512 /home/dev/certdir/kernel.key /home/dev/certdir/kernel.crt $2

