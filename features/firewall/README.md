## Feature: firewall
### Description
<website-feature>

This features adds a basic `nftables` based firewall to Garden Linux.
</website-feature>

### Features
This features adds a basic `nftables` based firewall to Garden Linux and is controlled by systemd.
The firewall rules can be adjusted by editing the corresponding rule file:
```
IPv4 and IPv6: /etc/nft.d/default.conf
```

#### Input
By default, only the following incoming rules are allowed:

 * tcp/22 [SSH]
 * state/related-established

#### Output
 * Open (not filtered)

#### Forward
 * Open (not filtered)

### Unit testing
This feature support unit tests and validates that the default incoming policy is set to drop. Additionally, all needed packages will be validated.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|None|
|excluded_features|None|
