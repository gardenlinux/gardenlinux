## Feature: vagrant
### Description
<website-feature>
This feature flag adds vagrant libvirt to the Garden Linux artifact.
</website-feature>

```
vagrant box add --name gardenlinux gardenlinux_libvirt.box
vagrant init gardenlinux
vagrant up --provider=libvirt
```

### Features
**Warning**: Never use this feature on production!

### Unit testing
This feature does not support unit tests.

### Meta
|||
|---|---|
|type|flag|
|artifact|None|
|included_features|None|
|excluded_features|None|
