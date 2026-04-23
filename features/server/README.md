---
title: "Feature: server"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/server/README.md
github_target_path: docs/reference/features/server.md
---

## Feature: server
### Description
<website-feature>
This server layer adds further services like `auditd`, `SELinux` and `systemd` for service management.
</website-feature>

### Features
This server layer adds further services like `auditd`, `SELinux` and `systemd` for service management.
Additional tools like `dnsutils`, `sudo`, `sysstat` etc. are installed.

### Unit testing
This features support unit testing and validates the installed packages, sshd configuration, systemd units etc.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|`base`, `ssh`,`_selinux`|
|excluded_features|None|
