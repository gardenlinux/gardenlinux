## Feature: lima
### Description
<website-feature>
This feature flag produces an image suitable for using with [lima](https://lima-vm.io)
</website-feature>

For the time being, this only supports `qemu` virtual machines.
Using `vz` is not supported.

How to use:

1. A gardenlinux image for LIMA is actioned to be built and uploaded weekly for arch AMD64 and ARM64

2. Create a LIMA VM with GardenLinux image:
  - No extra setup/download needed, if you have lima set up you can just use it as below 

```bash
  limactl create --name gardenlinux https://images.gardenlinux.io/gardenlinux.yaml
```

3. Start the VM: `limactl start gardenlinux`

4. Open a shell inside the VM: `limactl shell gardenlinux`


