#!/bin/sh

echo "signing $2"
/usr/lib/linux-kbuild-5.4/scripts/sign-file sha512 /kernel.key /kernel.crt $2

