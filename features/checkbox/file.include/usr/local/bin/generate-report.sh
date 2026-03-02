#!/bin/sh

mkdir -p /etc/xdg/autostart
mkdir -p /var/www/html/reports
chmod 755 /var/www/html/reports

checkbox-cli run --non-interactive --output-format html --output-file /var/www/html/reports/index.html 'com.canonical.certification::gardenlinux-test' 
