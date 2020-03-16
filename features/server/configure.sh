systemctl enable systemd-networkd
systemctl enable systemd-timesyncd
systemctl enable systemd-resolved
systemctl enable fail2ban
systemctl enable ferm
#systemctl enable systemd-machine-id-setup
#systemctl enable systemd-machine-id-commit
for i in $(ls /boot | grep vmlinuz | sed "s/vmlinuz-//"); do
	systemctl enable kexec-load@$i
done


cat << 'EOF' > /tmp/newmotd
  ____               _              _     _                  
 / ___| __ _ _ __ __| | ___ _ __   | |   (_)_ __  _   ___  __
| |  _ / _` | '__/ _` |/ _ \ '_ \  | |   | | '_ \| | | \ \/ /
| |_| | (_| | | | (_| |  __/ | | | | |___| | | | | |_| |>  < 
 \____|\__,_|_|  \__,_|\___|_| |_| |_____|_|_| |_|\__,_/_/\_\
 
Garden Linux 11 (based on Debian GNU/Linux 11)

EOF
cat /etc/motd >>/tmp/newmotd
cp /tmp/newmotd /etc/motd
