# Run Garden Linux Virtual Machines Locally Using Lima (Linux Machines)

[Lima (Linux Machines)](https://lima-vm.io) is a virtual machine lifecycle management tool that makes it trivial to run virtual machines on your local laptop.
Lima makes use of existing vm solutions such as QEMU or Apple Virtualization, and takes care of all the hard parts of configuration such as creating a user and mounting directories into the vm.

Garden Linux provides pre-built images suitable for use with Lima, but you can also build your own images.

Garden Linux images for Lima are published at https://images.gardenlinux.io

## How to use the pre-built image

You need to have `podman` and `lima` installed.

> [!NOTE]
> You need to have `podman` and `lima` installed.
> Garden Linux offers a lightweight container image that generates a ready-to-use Lima YAML manifest. This approach simplifies usage, as image URLs can be complex and difficult to construct manually. The script within the container automatically creates the correct URL and includes all necessary dependencies, making the process straightforward. The container outputs only the required YAML file for Lima; you may redirect this output to a file for review or modification as needed.

The pre-built images are intentionally minimal and do not include much of the additional software available in Garden Linux.
You can use `apt` to search and install additional software that is available for Garden Linux.

To get started, follow those instructions:

1. Create and start the VM


```bash
# for the latest nightly build, use:
podman run --rm ghcr.io/gardenlinux/gardenlinux/lima:latest | limactl start --name gardenlinux -
# for using a specific nightly build, specify the version numbers
podman run --rm ghcr.io/gardenlinux/gardenlinux/lima:latest --version 2066.0.0 --allow-nightly | limactl start --name gardenlinux -
# for using a release version, specify the version (note: as of December 2025, no released version has this feature yet, will work with the next major version of Garden Linux)
podman run --rm ghcr.io/gardenlinux/gardenlinux/lima:latest --version 21xx.1.0 | limactl start --name gardenlinux -
```

2. Open a shell inside the VM: `limactl shell gardenlinux`

## How to build your own image

If the pre-built image is not suitable for your needs, you can build your own image with the set of features you require.
For example, if you need the `python` and the `sapmachine` feature, you can build that using

1. Build an image: `./build lima-python-sapmachine`

2. Create the manifest.yaml file

```yaml
os: Linux
images:
  - location: /path/to/your/gardenlinux/.build/lima-python-sapmachine-[ARCH]-[VERSION]-[COMMIT_SHA].qcow2

containerd:
  system: false
  user: false
```

3. Create and start the VM: `cat manifest.yaml | limactl start --name=gardenlinux -`

4. Open a shell inside the VM: `limactl shell gardenlinux`

## Sample manifests

Lima allows to configure provisioning shell scripts in manifest files.

In [features/lima/samples](https://github.com/gardenlinux/gardenlinux/tree/main/features/lima/samples), you can find example scripts that might be useful depending on your use-case.
Depending on what you're planning to do, building a custom image might be better than using provisioning shell scripts.
