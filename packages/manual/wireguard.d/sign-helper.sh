#!/bin/sh

echo "signing $2"
/lib/modules/$1/build/scripts/sign-file sha512 /home/dev/certdir/kernel.key /home/dev/certdir/kernel.crt $2

