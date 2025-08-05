## Feature: lima
### Description
<website-feature>
This feature flag produces an image suitable for using with [lima](https://lima-vm.io)
</website-feature>

For the time being, this only supports `qemu` virtual machines.
Using `vz` is not supported.

Garden Linux images for Lima are published at https://images.gardenlinux.io

How to use the pre-built image:

1. Create and start the VM

```
limactl start --name gardenlinux https://images.gardenlinux.io/gardenlinux.yaml
```

2. Open a shell inside the VM: `limactl shell gardenlinux`

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

3. Create and start the VM: `cat manifest.yaml | limactl start --name=gardenlinux -`

4. Open a shell inside the VM: `limactl shell gardenlinux`

## Sample manifests

Lima allows to configure provisioning shell scripts in manifest files.

In [samples](./samples/), you can find example scripts that might be useful depending on your use-case.
Depending on what you're planning to do, building a custom image might be better than using provisioning shell scripts.
