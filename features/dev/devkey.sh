#!/bin/sh

ssh-keygen -b 2048 -f id_dev -N ''
mkdir -p copy/root/.ssh
chmod 700 copy/root/.ssh
mv id_dev.pub copy/root/.ssh/authorized_keys
chmod 600 copy/root/.ssh/authorized_keys
