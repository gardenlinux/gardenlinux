systemctl enable systemd-networkd
systemctl enable systemd-timesyncd
systemctl enable systemd-resolved
systemctl enable fail2ban
systemctl enable ferm
systemctl enable ssh-keygen
systemctl enable ssh-moduli

for i in $(ls /boot | grep vmlinuz | sed "s/vmlinuz-//"); do
	systemctl enable kexec-load@$i
done

update-ca-certificates
addgroup --system wheel

ln -sf /sbin/ip /bin/ip
ln -sf /sbin/ip /usr/bin/ip

