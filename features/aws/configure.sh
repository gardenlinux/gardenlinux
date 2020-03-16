#!/usr/bin/env bash 

sed -i "s/^#NTP=/NTP=instance-data.ec2.internal/g" /etc/systemd/system.conf
# add "nvme_core.io_timeout=4294967295" to GRUB_CMDLINE_LINUX
echo "TODO add GRUB paremeter"
