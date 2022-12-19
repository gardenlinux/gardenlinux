## Feature: firecracker
### Description
<website-feature>
This platform feature creates an artifact for firecracker (microVM) environments.
</website-feature>

### Features
This feature creates a firecracker (microVM) compatible image artifact that consists of two parts:

**Kernel**: `.vmlinux`

**Filesystem**: `.ext4`

### Unit testing
This platform feature supports unit testing and is based on the `firecracker` fixture to validate the applied changes according its feature configuration.

### Meta
|||
|---|---|
|type|platform|
|artifact|`.vmlinux`, `.ext4`|
|included_features|`server`|
|excluded_features|None|
