## Feature: _readonly

<website-feature> enable readonly </website-feature>

This feature enables a readonly root partition with dmverity, additionally a separate readonly /usr partition can also use dmverity.
If only /usr should be readonly and use dmverity, take a look at the next chapter to find an example for how to setup the fstab.mod for that case.

---

	Type: flag
	Included Features: server
#

## dmverity only for /usr with writable root partition

To only enable dmverity for /usr and have a writable root partition the fstab.mod must be adjusted accordingly. But keep in mind that
/etc/veritytab, that is containing the hash for the partition, most likely is located on a writable partition and therefore easy to modify.

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