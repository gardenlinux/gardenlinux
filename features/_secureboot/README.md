## Feature: _secureboot
### Description
<website-feature>
This feature flag adds secureboot to the Garden Linux artifact.
</website-feature>

### Features
This feature adds support for secureboot and requires UEFI enabled target systems. A 128MiB sized `/boot/efi` partition will be created.
Keys can be enrolled by running the script `/usr/sbin/enroll-gardenlinux-secureboot-keys`.

### Unit testing
Unit tests will ensure that `/boot/efi` is initially empty and all keys are present for enrollment (`pk.auth`, `kek.auth`, `db.auth`).

### Meta
|||
|---|---|
|type|flag|
|artifact|None|
|included_features|server|
|excluded_features|None|
