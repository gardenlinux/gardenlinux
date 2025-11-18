## Feature: lima
### Description
<website-feature>
This feature flag produces an image suitable for using with [lima](https://lima-vm.io)
</website-feature>

Garden Linux images for Lima are published with nightly or release

**How to use the pre-built image:**

1. Prerequisities
    - podman
    - access to gardenlinux-glrd.s3.eu-central-1.amazonaws.com

2. Create and start the VM

Lima image can be started with start-lima.py inside bin folder
```
# for help, use:
./bin/start-lima.py --help
```
```
# for the latest nightly image, use:
./bin/start-lima.py --name gardenlinux --version nightly --arch <arch>
```
```
# for the latest release, use:
./bin/start-lima.py --name gardenlinux --version latest --arch <arch>
```
```
# for a particular version, use:
./bin/start-lima.py --name gardenlinux --version <version> --arch <arch>
```

3. Open a shell inside the VM: `limactl shell gardenlinux`

**How to build your own image:**

1. Build an image: `./build lima`

2. Create the manifest.yaml file

```yaml
os: Linux
images:
  - location: /path/to/your/gardenlinux/.build/lima-[ARCH]-[VERSION]-[COMMIT_SHA].qcow2

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
