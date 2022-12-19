## Feature: gardener
### Description
<website-feature>

The gardener feature adjusts Garden Linux to fulfil the [gardener.cloud](https://gardener.cloud) requirements.
</website-feature>

### Features
The gardener feature adjusts Garden Linux to fulfil the `gardener.cloud` requirements and installs further package like `Docker` and `containerd`. By default, both systemd unit files are disabled and will be enabled by `Gardener` itself. Additionally, the `/usr` mount gets mounted in `ro` mode and nfs hardened.

### Unit testing
Unit tests are supported for this feature and will ensure that the groups are correctly defined, dmesg can be accessed by every user (Gardener requirement), all required packages are installed and the active LSM is switched from SELinux to AppArmor.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|server|
|excluded_features|None|
