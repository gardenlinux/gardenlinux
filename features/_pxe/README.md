## Feature: _pxe
### Description
<website-feature>
This flag feature creates an artifact for supporting PXE network boot of Garden Linux.
</website-feature>

### Features
This feature creates files meant to be booted via PXE network boot: `squashfs`, `kernel`, `initrd`, `initrd.unified` - initrd including squashfs, `boot.efi` - UKI.

### !!! IMPORTANT !!!
Please be aware of the fact that systemd-networkd-wait-online is configured to mark the system as online when at least one interface becomes online. 
This makes the boot process faster, but, on systems with multiple NICs on different network segments, that would mean that depending on the order in which the NICs get configured, the system will get marked as online but the squashfs fetching might still fail and the system will fail to boot.

#### Hint
Ignition Files can be used with PXE to inject information into the system at the first boot of Garden Linux. This includes creating users, groups, ssh keys, files, permissions and network configuration. This way machines can be defined in a declarative way.

See also:
- [iPXE Documentation @ ipxe.org](https://ipxe.org/docs)
- [iPXE Script Examples @ ipxe.org](https://ipxe.org/scripting)
- [Ignition Documentation @ fedoraproject.org](https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/#_ignition_overview)


### Unit testing
This feature does not support unit tests.

### Meta
|||
|---|---|
|type|flag|
|artifact|`squashfs`, `vmlinuz`, `initrd`, `initrd.unified`, `boot.efi`|
|included_features|`_ignite`|
|excluded_features|None|
