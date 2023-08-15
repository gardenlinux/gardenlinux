## Feature: lima
### Description
<website-feature>
This feature flag produces an image suitable for using with [lima](https://lima-vm.io)
</website-feature>

Build the image with `./build kvm-lima`

Example config (build image locally, adapt path, save config as `gardenlinux.yaml`):

```
images:
- location: "path/to/kvm-lima-amd64-today-local.raw"
  arch: "x86_64"
- location: "path/to/kvm-lima-arm64-today-local.raw"
  arch: "aarch64"
```

Example usage:

```
$ cat gardenlinux.yaml | limactl create --name=gardenlinux -
$ limactl start gardenlinux
$ limactl shell gardenlinux
```

Known limitations:

- Mounting host directories into the VM is not supported yet
