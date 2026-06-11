#!/bin/sh

mkdir -p /var/www/html/reports
chmod 755 /var/www/html/reports
mkdir -p /etc/xdg/autostart

# Run checkbox and write report to reports/index.html
# The root index.html placeholder (served by nginx) auto-refreshes until this appears
checkbox-cli run --non-interactive --output-format html --output-file /var/www/html/reports/index.html \
    'com.canonical.certification::gardenlinux-test' || true
