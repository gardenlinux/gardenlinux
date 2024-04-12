## Feature: lima
### Description
<website-feature>
This feature flag produces an image suitable for using with [lima](https://lima-vm.io)
</website-feature>

Example usage with a pre-built image:

```
$ limactl create --name=gardenlinux-today https://images.gardenlinux.io/kvm_curl-lima-today.yaml
$ limactl start gardenlinux-today
$ limactl shell gardenlinux-today
```

Known limitations:

- Mounting host directories into the VM is not supported yet
