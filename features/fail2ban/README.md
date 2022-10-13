# Fail2Ban

## General
Fail2Ban reads log file that contains password failure report and bans the corresponding IP addresses using firewall rules. It updates firewall rules to reject the IP address.

## Overview
By default, `fail2ban` will be installed by `ssh` as a dependency. However, it may be safely removed if the operator does not want to use it.

## Configuration

### Defaults
Beside the default upstream configuration only the backend for `systemd` got changed.

**Note**: You should change the email configuration to your needs!

### Changes
Changes to the configuration can be done within the [jail.conf](file.include/etc/fail2ban/jail.conf) file.

### Active services
Currently, only the `ssh` service is activated. Further backends may be activated by editing the [jail.conf](file.include/etc/fail2ban/jail.conf) config file to your needs.