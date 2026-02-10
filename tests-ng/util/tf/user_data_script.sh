#!/usr/bin/env bash

systemctl enable --now ssh

mkdir /run/gardenlinux-tests
mount /dev/disk/by-label/GL_TESTS /run/gardenlinux-tests
