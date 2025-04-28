## Feature: lima
### Description
<website-feature>
This feature flag produces an image suitable for using with [lima](https://lima-vm.io)
</website-feature>

For the time being, this only supports `qemu` virtual machines.
Using `vz` is not supported.

How to use:

1. Build an image: `./build kvm-lima`

2. Create the manifest.yaml file

```yaml
vmType: qemu
os: Linux
images:
  - location: /path/to/your/gardenlinux/.build/kvm-lima-[ARCH]-[VERSION]-[COMMIT_SHA].qcow2

containerd:
  system: false
  user: false
```

3. Create the VM: `cat manifest.yaml | limactl create --name=gardenlinux -`

4. Start the VM: `limactl start gardenlinux`

5. Open a shell inside the VM: `limactl shell gardenlinux`
