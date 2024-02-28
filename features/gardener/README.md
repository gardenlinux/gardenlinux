## Feature: gardener
### Description
The gardener feature adjusts Garden Linux to fulfil the [gardener.cloud](https://gardener.cloud) requirements.
As Garden Linux is the Container Node OS for Gardener, that's also where the "Garden" part in the name originates.

### Features
The `gardener` feature adjusts Garden Linux to fulfil the `gardener.cloud` requirements:
- Installs package `docker.io`
  - Needed for handling the [hyperkube](https://github.com/gardener/hyperkube) downloads in Gardener
- installs package `containerd`
  - This is a duplicate of the ContainerHost (chost) feature, but as `containerd` is a fundamental requirement of Gardener it is also included in this feature
- By default, systemd unit files for `docker.io` and `containerd` are disabled and will be enabled by Gardener itself.
- Installs default requirements for Gardener / Kubernetes `apparmor`, `ethtool`, `ipvsadm`, `socat`, `ebtables`
  - This is very similar to the KubernetesHost (khost) feature of GardenLinux itself but adapted to Gardener needs
- Installs filesystem clients `btrfs-progs`, `xfsprogs`, `nfs-common`, `cifs-utils` to support common Gardener remote file system needs
- Installs standard tools like `jq`, `curl` and `netcat` as needed by Gardener

### Security
The default configuration is to run `/usr` as a separate mount (different to other Garden Linux incarnations) and to mount `/usr` in `ro` (readonly) mode.
This is ensures a very simple but effective level of immutability.
If a node is 'rolled' in Gardener terms (means the node is recreated), Gardener always reimages the node over the cloud provider.
This ensures a constant image quality and no local modifications.
A node might reboot in rare circumstances (for example when a bug occurs), but this is never automatically done by Gardener.
Automated image recreation is not needed.

The typical network file system clients like `cifs` or `nfs` are extra hardened to circumvent the most common bugs.

### Unit testing
Unit tests are supported for this feature and will ensure that the groups are correctly defined, dmesg can be accessed by every user (Gardener requirement), all required packages are installed and the active LSM is switched from SELinux to AppArmor.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|server|
|excluded_features|None|
