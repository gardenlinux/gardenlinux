#!/bin/sh

ssh-keygen -b 2048 -f id_dev -N ''
cp -p id_dev.pub file.include/authorized_keys
