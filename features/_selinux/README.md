## Feature: _selinux
### Description
<website-feature>
This feature flag adds SELinux extended attributes to the Garden Linux artifact.
</website-feature>

### Features
This feature adds support for SELinux attributes files on the target systems.

### Unit testing
This feature checks if Linux Security Module (LSM) has been correctly set to selinux on the kernel command line
and if the required selinux policy rules have been installed.

### Meta
|||
|---|---|
|type|flag|
|artifact|None|
|included_features|None|
|excluded_features|None|
