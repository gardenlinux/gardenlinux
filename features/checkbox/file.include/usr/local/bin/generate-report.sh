#!/bin/sh

mkdir -p /var/www/html/reports
chmod 755 /var/www/html/reports

# Run checkbox using launcher config which handles output and disables restart strategy
checkbox-cli launcher /etc/checkbox/gardenlinux-launcher.conf || true
