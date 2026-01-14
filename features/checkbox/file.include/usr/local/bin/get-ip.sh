#!/bin/sh
IP=$(ip -4 route get 1.1.1.1 | awk '{print $7; exit}')
checkbox-cli run --non-interactive --output-format html --output-file /var/www/html/reports/index.html 'com.canonical.certification::gardenlinux-test' 

cat >/etc/issue <<EOF
Welcome to Garden Linux HW Testing Image

Reports available at:
  http://$IP/reports/

EOF

