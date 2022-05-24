# Feature: cis_firewall
This feature adds a basic `iptables` based firewall to Garden Linux. `Garden Linux CIS Firewall`
 is managed by `systemd` by the following systemd unit files:

* gardenlinux-fw-ipv4
* gardenlinux-fw-ipv6

The firewall rules can be adjusted by editing the corresponding rule file:
```
IPv4: /etc/firewall/ipv4_gl_default.conf
IPv6: /etc/firewall/ipv6_gl_default.conf
```

By default, only the following rules are allowed:

 * tcp/22 [SSH]
 * tcp/2222 [SSH for unit tests]
 * tcp/2223 [SSH for unit tests]
 * state/related-established
