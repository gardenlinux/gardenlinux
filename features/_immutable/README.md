## Feature: _immutable

<website-feature> add immutability </website-feature>

This feature adds immutability to Garden Linux. The Garden Linux image only contains a partition for the EFI bootloader and a USR partition. The USR partition is readonly and has `dm-verity` enabled. The image does NOT contain a ROOT partition, instead the initramfs contains the tools to initialize the ROOT partition on boot. By default the ROOT partition is deleted on `poweroff` or `halt`, but NOT on `reboot`. The ROOT partition is writable.

To persist the ROOT partition create the file `/etc/immutability.disabled`. This disables the deletion of the ROOT partition during shutdown.

To initialize the ROOT partition the systemd-repart and systemd-tmpfiles modules and their configurations are added to the initramfs. Additionally the `mkfs.ext4` binary and a modified `systemd-tmpfiles-setup.service` are needed to make the ROOT partition initialization work.

The dm-verity hash for the USR partition is added to the kernel commandline with the `usrhash=` option and is needed, without this option the boot process gets stuck and the ROOT partition is not initialized.

Also the feature disables `ignition` and `ignition` is not added to the initramsf as it causes a systemd dependencies loop with the modified `systemd-tmpfiles-setup.service` and breaks the boot process.