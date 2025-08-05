## Feature: lima
### Description
<website-feature>
This feature flag produces an image suitable for using with [lima](https://lima-vm.io)
</website-feature>

For the time being, this only supports `qemu` virtual machines.
Using `vz` is not supported.

Garden Linux images for Lima are published at https://images.gardenlinux.io

How to use the pre-built image:

1. Create the VM

```
limactl create --name gardenlinux https://images.gardenlinux.io/gardenlinux.yaml
```

2. Start the VM: `limactl start gardenlinux`

3. Open a shell inside the VM: `limactl shell gardenlinux`

How to build your own image:

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
