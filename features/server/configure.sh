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

echo "Garden Linux (based on Debian GNU/Linux 10)" >/tmp/newmotd
cat /etc/motd >>/tmp/newmotd
cp /tmp/newmotd /etc/motd
