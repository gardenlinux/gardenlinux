## Feature: gardener
### Description
The gardener feature adjusts Garden Linux to fulfil the [gardener.cloud](https://gardener.cloud) requirements. (actually that is the reason why Garden Linux has the theming "garden" in the name)

### Features
The gardener feature adjusts Garden Linux to fulfil the `gardener.cloud` requirements:
- installs package `Docker` (needed for handling the hyperkube downloads in Gardener)
- installs package `containerd` (actually that is a duplicate from the ContainerHost (chost) feature, but there is an explicit requirement for Containerd in Gardener since it is the base technology.
- By default, systemd unit files for `Docker` and `containerd` are disabled and will be enabled by Gardener itself.
- installs default requirements for Gardener / Kubernetes `apparmor`, `ethtool`, `ipvsadm`, `socat`, `ebtables`. This is very similar to the KubernetesHost (khost) feature of GardenLinux itself but special adapted to Gardener needs.
- installs filesystem clients `btrfs-progs`, `xfsprogs`, `nfs-common`, `cifs-utils` to support common Gardener remote file system needs.
- other then that Gardener standard tooling like `jq`, `curl` and `netcat` is needed

### Security
The default configuration is to run `/usr` as a separate mount (different to other Gardenlinux incarnations) and to mount `/usr` in `ro` (readonly) mode. This is ensures a very simple but effective level of immutability.
If a node is 'rolled' in Gardener terms (means recreated), Gardener always reimages the node over the cloud provider. This ensures a constant image quality and no local modifications.
In rare circumstances Gardener nodes reboot (in case of a bug e.g. but never automated by gardener) so the automated image recreation is not needed.

The typical network file system clients like cifs or nfs are extra hardened to circumvent the most common bugs

### Unit testing
Unit tests are supported for this feature and will ensure that the groups are correctly defined, dmesg can be accessed by every user (Gardener requirement), all required packages are installed and the active LSM is switched from SELinux to AppArmor.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|server|
|excluded_features|None|
