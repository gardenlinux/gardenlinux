## Feature: ssh
### Description
<website-feature>
This ssh layer adds the OpenSSH server with sshguard.
</website-feature>

### Features
This ssh layer adds the OpenSSH server with sshguard.

Sshguard uses `nftables` which is installed and managed by the [`firewall`](../firewall/) feature.
If the `firewall` feature is excluded, but `iptables` is available, sshguard will use `iptables`.
If neither are available, sshguard is disabled.

#### Configs
Services may be modified to the users need.

OpenSSH server: `file.include/etc/ssh/sshd_config`

### Unit testing
This feature supports unit tests that will validate the correct configuration of the openssh server. These checks can be performed on any target platform.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|`firewall`|
|excluded_features|None|
