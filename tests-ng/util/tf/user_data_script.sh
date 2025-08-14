#!/usr/bin/env bash

systemctl enable --now ssh

mkdir /var/tmp/gardenlinux-tests
mount /dev/disk/by-label/GL_TESTS /var/tmp/gardenlinux-tests
