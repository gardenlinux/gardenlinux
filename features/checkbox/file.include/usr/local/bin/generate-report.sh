#!/bin/sh

mkdir -p /var/www/html

# Write "in progress" placeholder — nginx serves this until tests complete
cp /var/www/html/index.html /var/www/html/index.html.bak 2>/dev/null || true

# Run checkbox and write report directly over the placeholder when complete
checkbox-cli run --non-interactive --output-format html --output-file /var/www/html/index.html \
    'com.canonical.certification::gardenlinux-test' || true
