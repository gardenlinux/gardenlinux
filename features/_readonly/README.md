## Feature: _readonly
### Description
<website-feature>
This flag feature adds a read only mode to the Garden Linux artifact.
</website-feature>

### Features
This feature enables a read only root partition together with `dm-verity`. By using `dm-verity`, the integrity of a block device is checked against a hash tree. Consequently, this ensures files have not changed between reboots or during runtime otherwise the access to those files would fail. An OverlayFS for `/var` and `/etc` ensures, that the Operating System stays operational during runtime.

More information about `dm-verity` can be found [here](https://www.kernel.org/doc/html/latest/admin-guide/device-mapper/verity.html).

Additionally, a separate readonly `/usr` partition is configured to be used with `dm-verity`, too.

If only `/usr` should be configured this way (readonly & dm-verity) without enabling this feature for the whole root parition, take a look at the next chapter to find an example for how to setup the [fstab.mod](https://github.com/gardenlinux/gardenlinux/blob/main/features/_readonly/fstab.mod) for this case.

### dm-verity only for /usr with writable root partition
In order to only enable dm-verity for `/usr` and have a writable root partition the [fstab.mod](https://github.com/gardenlinux/gardenlinux/blob/main/features/_readonly/fstab.mod) must be adjusted accordingly. But keep in mind that `/etc/veritytab`, which is containing the hash for the partition, most likely is located on a writable partition and therefore easy to modify.

NOTE: The sed statement does not remove the root partition from the fstab!

```fstab.mod
#!/usr/bin/env bash
set -Eeuo pipefail

# delete any predefinition of a overlay, usr and EFI partition
sed '/^[^[:space:]]\+[[:space:]]\+\/overlay[[:space:]]\+/d;/^[^[:space:]]\+[[:space:]]\+\/usr[[:space:]]\+/d;/^[^[:space:]]\+[[:space:]]\+\/boot\/efi[[:space:]]\+/d'

# make usr a readonly setup
printf "LABEL=EFI          /boot/efi    vfat      umask=0077   type=uefi,size=96MiB\n"
printf "LABEL=USR          /usr         ext4      ro           verity\n"
```

### Unit testing
Unit tests will ensure that `/boot/efi` is initially empty and all keys are present for enrollment (`pk.auth`, `kek.auth`, `db.auth`).

### Meta
|||
|---|---|
|type|flag|
|artifact|None|
|included_features|None|
|excluded_features|None|
