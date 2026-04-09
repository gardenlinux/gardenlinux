## Feature: stigPartition
### Description
<website-feature>

This subfeature manages the partition layout according to the DISA STIG requirements. This features depends on its parents feature `stig`.
</website-feature>

### Features
Regarding `STIG` requirements, further options like `noexec`, `nodev` must be set for several mounts. Therefore, a default partition layout is shipped by this feature. The size for any mount can be adjusted:

**FSTab**
```
# <file system>    <dir>              <type>    <options>                              <args>
LABEL=EFI          /boot/efi          vfat      umask=0077                             type=uefi
LABEL=ROOT         /                  ext4      rw,errors=remount-ro,prjquota,discard  size=1024MiB
LABEL=HOME         /home              ext4      defaults,nosuid,noexec,nodev           size=64MiB
LABEL=VAR          /var               ext4      defaults,nosuid,noexec,nodev           size=128MiB
LABEL=VARTMP       /var/tmp           ext4      defaults,nosuid,noexec,nodev           size=64MiB
LABEL=VARLOG       /var/log           ext4      defaults,nosuid,noexec,nodev           size=128MiB
LABEL=VARLOGAUD    /var/log/audit     ext4      defaults,nosuid,noexec,nodev           size=64MiB
```

`/tmp` will be handled by a systemd unit file and be created with `STIG`-compliant options:

```
Options=mode=1777,strictatime,nosuid,nodev,noexec
```

### Unit testing
Unit tests are only supported by its parent feature `stig`. See also [../stig/README.md](../stig/README.md).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|stig|
|excluded_features|None|
