#!/usr/bin/env bash 

sed -i "s/^#NTP=/NTP=instance-data.ec2.internal/g" /etc/systemd/system.conf
# add "nvme_core.io_timeout=4294967295" to GRUB_CMDLINE_LINUX
echo "TODO add GRUB paremeter"

# growpart is done in initramfs, growroot by systemd
mv /etc/cloud/cloud.cfg /etc/cloud/cloud.cfg.bak
cat /etc/cloud/cloud.cfg.bak | grep -v "^ - growpart$" | grep -v "^ - resizefs$" >/etc/cloud/cloud.cfg  
rm /etc/cloud/cloud.cfg.bak 