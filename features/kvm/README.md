## Feature: kvm
### Description
<website-feature>
This platform feature creates an artifact for KVM/QEMU.
</website-feature>

### Features
This feature creates a KVM/QEMU compatible image artifact as a `.qcow2` file.

### Unit testing
This platform feature supports unit testing and is based on the `kvm` fixture to validate the applied changes according its feature configuration.
Next to this, `kvm` fixture is the base platform to perform local unit tests that may require a running OS.

### Meta
|||
|---|---|
|type|platform|
|artifact|`.raw`,`.qcow2`|
|included_features|`server`|
|excluded_features|None|
