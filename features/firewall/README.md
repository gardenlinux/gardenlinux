# Feature: cis_firewall
This feature adds a basic `nftables` based firewall to Garden Linux. `Garden Linux Firewall`
 is managed by `systemd` by the default systemd unit shipped with nftables.

The firewall rules can be adjusted by editing the corresponding rule file:
```
IPv4 and IPv6: /etc/nft.d/default.conf
```

By default, only the following rules are allowed:

 * tcp/22 [SSH]
 * state/related-established
