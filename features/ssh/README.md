## Feature: ssh
### Description
<website-feature>
This ssh layer adds the OpenSSH server with Fail2ban.
</website-feature>

### Features
This ssh layer adds the OpenSSH server with Fail2ban. Fail2ban uses `nftables` which is installed and managed by the [firewall](../firewall/) feature.

#### Configs
Services may be modified to the users need.

OpenSSH server: `file.include/etc/ssh/sshd_config`

Fail2ban: `file.include/etc/fail2ban/jail.conf`

### Unit testing
This feature supports unit tests that will validate the correct configuration of the openssh server. These checks can be performed on any target platform.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|`firewall`|
|excluded_features|None|
