#!/bin/sh

ssh-keygen -b 2048 -f id_dev -N ''
cp id_dev.pub file.include/authorized_keys
