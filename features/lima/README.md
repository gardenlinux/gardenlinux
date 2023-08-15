## Feature: lima
### Description
<website-feature>
This feature flag produces an image suitable for using with [lima](https://lima-vm.io)
</website-feature>

Example config:

```
images:
- location: "path/to/kvm-lima-amd64-today-local.raw"
  arch: "x86_64"
- location: "path/to/kvm-lima-arm64-today-local.raw"
  arch: "aarch64"
```

Known limitations:

- Mounting host directories into the VM is not supported yet
