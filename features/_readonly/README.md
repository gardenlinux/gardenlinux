## Feature: _readonly
### Description
<website-feature>
This feature flag adds readonly mode to the Garden Linux artifact.
</website-feature>

### Features
This feature enables a readonly root partition together with `dm-verity`. By using `dm-verity`, the integrity of a block device is checked against a hash tree. Consequently, this ensures files have not changed between reboots or during runtime otherwise the access to those files would fail. An OverlayFS for `/var` and `/etc` ensures, that the Operating System stays operational during runtime.

More information about `dm-verity` can be found [here](https://www.kernel.org/doc/html/latest/admin-guide/device-mapper/verity.html).

Additionally, a separate readonly `/usr` partition is configured to be used with `dm-verity`, too.

If only `/usr` should be configured this way (readonly & dm-verity) without enabling this feature for the whole root partition, take a look at the chapter [dm-verity only for /usr with writable root partition](#dm-verity-only-for-usr-with-writable-root-partition) to find an example for how to setup the [fstab.mod](https://github.com/gardenlinux/gardenlinux/blob/main/features/_readonly/fstab.mod) for this case.

---

	Type: flag
	Included Features: server


## resizable /var partition

When `/var` is writable via the OverlayFS it causes problems when containerd is used. Therefore it is necessary to have a separate writable `/var` partition that is not an OverlayFS and it should also be easily resizable to be able to store container images as needed. When `/var` is the resizable partition the content of `/var` will be remove during build. To make sure `/var` is properly initialized a systemd-tmpfiles configuration exists in the `_readonly` feature. Additionally every feature that needs files in `/var` has a systemd-tmpfiles configuration as well, to create files and directories as needed.
Add the following line to the `fstab.mod` to create a Garden Linux image with a separate `/var` partition.

```
printf "LABEL=VAR          /var         ext4      rw,x-systemd.growfs          resizable,type=4d21b016-b534-45c2-a9fb-5c16e091fd2d\n"
```
* `x-systemd.growfs`: Instructs systemd-growfs to grow the filesystem to the size of the partition.
* `resizable`: Tells the `bin/makepart` script to move this partition to the end of the partition table to make the partition easily resizable.
* `type=4d21b016-b534-45c2-a9fb-5c16e091fd2d`: Helps systemd-repart to identify the partition and enlarge the partition.

## dm-verity only for /usr with writable root partition

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
