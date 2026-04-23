---
title: "Feature: vhost"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/vhost/README.md
github_target_path: docs/reference/features/vhost.md
---

## Feature: vhost
### Description
<website-feature>
The vhost feature adjusts Garden Linux to support running virtual workloads in KVM/libvirt.
</website-feature>

### Features
The vhost feature adjusts Garden Linux to support running virtual workloads in KVM/libvirt and installs and configures all related packages (regarding the used hardware architecture) and tools.

### Unit testing
To be fully compliant these unit tests validate the extended capabilities on `gstreamer`, the installed packages, correctly defined suids and sgids as well as the systemd unit files.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|server|
|excluded_features|None|
