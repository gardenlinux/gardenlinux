## Feature: _pxe
### Description
<website-feature>
This feature flag creates artifactd for PXE network boot of Garden Linux.
</website-feature>

### Features
This feature creates files meant to be booted via PXE Networkboot: .squashfs, .vmlinuz and .initrd.

#### Hint
Ignition Files can be used with PXE to inject information into the System at the first boot of Garden Linux. This includes Creating Users, Groups, SSH-Keys, Files, Permissions, Network Configuration. This way Machines can be defined in a declarative way.

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
|artifact|`.squashfs`, `.vmlinuz`, `.initrd`|
|included_features|_ignite|
|excluded_features|None|
