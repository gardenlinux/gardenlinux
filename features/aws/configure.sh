#!/usr/bin/env bash 

# AWS has an own time server
sed -i "s/^#NTP=/NTP=instance-data.ec2.internal/g" /etc/systemd/system.conf

# AWS DNS does not support DNSSEC
sed -i 's/^#DNSSEC=allow-downgrade/DNSSEC=false/g' /etc/systemd/resolved.conf

# growpart is done in initramfs, growroot by systemd
mv /etc/cloud/cloud.cfg /etc/cloud/cloud.cfg.bak
cat /etc/cloud/cloud.cfg.bak | grep -v "^ - growpart$" | grep -v "^ - resizefs$" | grep -v "^ - ntp$" >/etc/cloud/cloud.cfg  
rm /etc/cloud/cloud.cfg.bak

#systemctl enable cloud-init
