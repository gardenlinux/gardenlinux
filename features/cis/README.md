# !!WIP!! WORK IN PROGRESS !!
## This feature is not yet finalized!!
# CIS
## General
The [Garden Linux](https://gardenlinux.io/) [CIS](https://www.cisecurity.org) unit test is [Debian-CIS](https://github.com/ovh/debian-cis) (created by [OVH](https://github.com/ovh)) based. This test framework is mostly based on recommendations of [CIS (Center for Internet Security)](https://www.cisecurity.org) benchmarks for [Debian GNU/Linux](https://www.debian.org). However, Garden Linux may fulfill them in a slightly different way. This becomes important for unit testing where ACL's like `AppArmor` are replaced by `SELinux` (which is also accepted by CIS benchmarks). `CIS`
 related unit tests can be performed on any cloud platform (see also [../../tests/README.md](../../tests/README.md)) except of `chroot`.

## Overview
This `cis` feature represents a meta feature that includes multiple sub features. Most sub features are prefixed by `cis_`. Working with sub features provides an easy overview, adjustment and administration for each sub feature. While only including all sub features fits the CIS benchmarks, it is in an operators decision to adjust sub features to his needs. This allows changes to be as near as possible to `CIS`, even it may not fit the `CIS` benchmarks.

Sub features are included by the `cis/info.yaml` configuration file. Sub features **can not** be used as a standalone feature and always depend on `cis`. The `cis` feature currently exists of the following sub features:

| Feature Name | Description |
|---|---|
| aide | Installs the host-based intrusion detection system Aide |
| cis_audit | Configuring the `auditd` daemon |
| firewall | Adding/Installing the `Garden Linux CIS Firewall` |
| cis_modprobe | Removing/Blacklisting Kernel modules |
| cis_os | Adjusting basic settings for the OS (Operating System) |
| cis_packages | Installing/Removing packages that may be needed or unwanted |
| cis_partition | Providing a default partition layout |
| cis_sshd | Adjusting the SSHd configuration |
| cis_sysctl | Adjusting further sysctl options (e.g. deactivates IPv6) |

### Feature: cis_aide
This feature installs the host-based intrusion detection system Aide, adds a configuration file for Aide, adds a systemd unit that creates an Aide database at boot time if it doesn't exist and adds a cronjob to /etc/cron.d to run Aide every night.

### Feature: cis_audit
This feature adjust the basic `auditd` configuration regarding the logging of events. This includes changes of date/time, sudo logging, as well as options how to proceed if disk space get low or is full.

### Feature: cis_firewall
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

### Feature: cis_modprobe
This feature removes/blacklists unwanted und not needed Kernel modules. Regarding `CIS` benchmark, `fat` should also be blacklisted. However, this is needed for booting `UEFI`.

The following modules are blacklisted:
* cramfs
* dccp
* freevxfs
* jffs2
* rds
* sctp
* squashfs
* tipc
* udf

### Feature: cis_packages
This feature installs needed packages as well as it removed unwanted packages. While Garden Linux base is a really slim image, no packages need to be removed.

The following packages are installed:
* git
* syslog-ng
* libpam-pwquality
* tcpd

### Feature: cis_partition
Regarding `CIS` benchmarks, further options like `noexec`, `nodev`must be set for several mounts. Therefore, a default partition layout is shipped by this feature. The size for any mount can be adjusted:

**FSTab**
```
# <file system>    <dir>              <type>    <options>                              <args>
LABEL=EFI          /boot/efi          vfat      umask=0077                             type=uefi
LABEL=ROOT         /                  ext4      rw,errors=remount-ro,prjquota,discard  size=1024MiB
LABEL=HOME         /home              ext4      defaults,nosuid,noexec,nodev           size=64MiB
LABEL=VAR          /var               ext4      defaults,nosuid,noexec,nodev           size=128MiB
LABEL=VARTMP       /var/tmp           ext4      defaults,nosuid,noexec,nodev           size=64MiB
LABEL=VARLOG       /var/log           ext4      defaults,nosuid,noexec,nodev           size=128MiB
LABEL=VARLOGAUD    /var/log/audit     ext4      defaults,nosuid,noexec,nodev           size=64MiB
```

`/tmp` will be handled by a systemd unit file and be created with `CIS`complaint options:

```
Options=mode=1777,strictatime,nosuid,nodev,noexec
```

### Feature: cis_sshd
This feature only adjusts the `sshd_config` to fit the `CIS` benchmark requirements.

### Feature: cis_systcl
This feature sets further `sysctl` options. This options are mostly IPv4 and IPv6 related. Keep in mind that this deactivates the IPv6 support in default.

## Unit Tests
The [CIS](https://www.cisecurity.org) unit test is [Debian-CIS](https://github.com/ovh/debian-cis) (created by [OVH](https://github.com/ovh)) based. This test framework is mostly based on recommendations of [CIS (Center for Internet Security)](https://www.cisecurity.org) benchmarks for [Debian GNU/Linux](https://www.debian.org). This tests will be proceeded for artifacts that are built with `CIS` feature and will validate all options, whether a sub feature is not included.

However, Garden Linux may fulfill them in a slightly different way. While the recommended way for ACL for Debian based distributions is `AppArmor`, Garden Linux used `SELinux`. As a result, `AppArmor` tests need to be whitelisted, as well as new `SeLinux` tests created.

Tests can be whitelisted by placing a `.cfg` file with equal name of the test in [test/conf.d](test/conf.d). More information can be found in [test/conf.d/README.md](test/conf.d/README.md).

Additional tests can be be included by placing an executable script nn [test/check_scripts](test/check_scripts). More information can be found in [test/check_scripts/README.md](test/check_scripts/README.md).
