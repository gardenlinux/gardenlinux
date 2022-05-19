# !!WIP!! WORK IN PROGRESS !!
## This feature is not yet finalized!!
# FedRAMP 
## Overview
This `FedRAMP` feature represents a meta feature that includes multiple sub features like `aide` or `firewall`. Working with sub features provides an easy overview, adjustment and administration for each sub feature. While only including all sub features fullfills the needed requirements for `FedRAMP`, it is in an operators decision to adjust sub features to his needs. This allows changes to be as near as possible to `FedRAMP`, even it may not fit the `FedRAMP` requirements.

Sub features are included by the `fedramp/info.yaml` configuration file. 

| Feature Name | Description |
|---|---|
| aide | Installs the host-based intrusion detection system Aide |
| firewall | Adding/Installing the `Garden Linux CIS Firewall` |

### Feature: aide
This feature installs the host-based intrusion detection system Aide, adds a configuration file for Aide, adds a systemd unit that creates an Aide database at boot time if it doesn't exist and adds a cronjob to /etc/cron.d to run Aide every night.

### Feature: firewall
This feature adds a basic `iptables` based firewall to Garden Linux. `Garden Linux Firewall`
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

## Unit Tests
The `FedRAMP` unit test is based on a simple [simple shell script](tests/test.sh) and is executed by a `PyTest` wrapper. This tests will be proceeded for artifacts that are built with `FedRAMP` feature and will validate all options, whether a sub feature is not included.
