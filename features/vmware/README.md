---
title: "Feature: vmware"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/vmware/README.md
github_target_path: docs/reference/features/vmware.md
---

## Feature: vmware
### Description
<website-feature>
This platform feature creates an artifact for VMWare platforms.
</website-feature>

### Features
This feature creates an VMWare platform compatible image artifact as an `.ova` file. During the build `.raw`, `.vmdk` and the converted `.ova` artifacts are created.

All artifacts include further tools for orchestrating the image like `cloud-init` and `open-vm-tools`.

Additionally, further changes for `growpart`, `ntp` etc. are applied and validated.

### Unit testing
This platform feature supports unit testing and is based on the `chroot` and `kvm` fixture to validate the applied changes according its feature configuration.

 Testing of specific units can be avoided by placing the `non_container` fixture.
### Meta
|||
|---|---|
|type|platform|
|artifact|`.vmdk`,`.ova`|
|included_features|cloud|
|excluded_features|None|