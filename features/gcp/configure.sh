#!/usr/bin/env bash

sed -i "s/^#NTP=/NTP=metadata.google.internal/g" /etc/systemd/system.conf

# This is done by systemd-neworkd, so we don't need it
systemctl disable google-network-daemon.service
