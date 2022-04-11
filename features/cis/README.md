# CIS Compliance Check
This feature (`cis`) is optional and adds [CIS](https://www.cisecurity.org) compliance to Garden Linux artifact images and performs further CIS compliance checks afterwards (only if tests are enabled).

## Usage
### General
This feature should be used as the last one in the build list in combination with additional features. However, this feature uses `dropin` directories where files from other features could also be placed. While creating this feature we gave all files the highest filename for the last execution but we still highly recommand to perform the provided unit tests after each built. Additionally, this may impact further unit tests from different features (e.g. validating cipher configs etc.).
### Configuration
**IMPORTANT:** While this features provides the nessescary tools, additional configuration still need to be adjusted to your own needs. Please make sure to adjust at least the following configurations:
#### syslog-ng
 * Define remote syslog host
 * Define remote syslog ACL

#### Auditd

#### Alias entry
 * Set correct aliases in: /etc/aliases

## (Unit) Tests for Compliance Check
If (unit) tests are enbaled additional frameworks will perform further CIS compliance checks. This can be done just after the built (if tests are enabled) or manually by the given [gardenlinux/tests/](../../../tests/README.md) pipeline. In every case, a running system will be needed. If no cloud platform account is present, this can also be done on a local `KVM` platform. The compliance checks are based on the following tools:
 * https://github.com/ovh/debian-cis
 * https://cisofy.com/lynis/

## Services
### Garden Linux CIS Firewall
For further CIS compliance a new Garden Linux service called `Garden Linux CIS Firewall` is introduced. This service manages firewall rules and will be automatically started by `systemd`. IPv4 and IPv6 protocols will be managed in dedicated ways. Therefore, two unit files are present:

 * gardenlinux-fw-ipv4
 * gardenlinux-fw-ipv6

The firewall rules can be adjusted by editing the corresponding rules file:
```
IPv4: /etc/firewall/ipv4_gl_default.conf
IPv6: /etc/firewall/ipv6_gl_default.conf 
```

In default, only the following rules are allowed:

 * tcp/22 [SSH]
 * tcp/2222 [SSH for unittests]
 * tcp/2223 [SSH for unittests]
 * state/related-established

## Whitelisting CIS related (Unit) Tests
(Unit) tests obtain their coonfigs from [cis/test/conf.d/](test/conf.d/). You may modify, delete or add additional whitelist entries for your needs. There is no need to adjust any pipeline code.

### Currently Whitelisted Checks
The following CIS compliance checks are currently whitelisted:
| Name | Reason |
|---|---|
| 1.1.1.7_restrict_fat | This will be needed to mount `/boot/efi` for cloud images |
| 1.9_install_updates | We want to validate a specific given artifact |
| 2.2.1.1_use_time_sync | `systemd-timesync` will be used for time synchronisation |
| 2.2.1.3_configure_chrony | `systemd-timesync` will be used for time synchronisation |
| 2.2.1.4_configure_ntp | `systemd-timesync` will be used for time synchronisation |
| 3.1.1_disable_ipv6 | Garden Linux should be cappable of IPv6 |
| 4.2.1.5_syslog-ng_remote_host | Syslog remote host is user specific and must be defined by the local operator |
| 4.2.1.6_remote_syslog-ng_acl | Remote syslog ACL is user specific and must be defined by the local operator |
| 4.4_logrotate_permissions | Further configs are included by a dropin directory |
| 5.1.1_enable_cron | `systemd-generator` will be used instead of `cron` |
| 99.99_check_distribution | Garden Linux is Debian testing based |
