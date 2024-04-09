The build system utilises the [gardenlinux/builder](https://github.com/gardenlinux/builder) to create customized Linux distributions. 
[gardenlinux/gardenlinux](https://github.com/gardenlinux/gardenlinux) is maintained by the Garden Linux team, highlighting specialized "features" available for other projects.

## Build Requirements

- **Memory:** The build process may require up to 8GiB of memory, depending on the selected targets. If your system has insufficient RAM, configure swap space accordingly.
- **Container Engine:** The Builder has minimal dependencies and only requires a working container engine. You have two options:
  - **Rootless Podman:** It's recommended to use rootless Podman. Please refer to the [Podman rootless setup guide](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md) for instructions on setting it up.
  - **Sudo Podman:** Alternatively, you can use Podman with sudo for elevated privileges.

To ensure a successful build, please refer to the [Build Requirements section](https://github.com/gardenlinux/builder#requirements) in the `gardenlinux/builder` repository.


##  Build

To initiate a build, use the command:
```shell
./build ${platform}-${feature}_${modifier}
```

Where:
- `${platform}` denotes the desired platform (e.g., kvm, metal, aws).
- `${feature}` represents a specific feature from the `features/` folder.
- `${modifier}` is an optional modifier from the `features/` folder, prefixed with an underscore "_".

You can combine multiple platforms, features, and modifiers as needed.

Example:
```shell
./build kvm-python_dev
```

The build script fetches the required builder container and manages all internal build steps. By default, it uses rootless podman, but you can switch to another container engine with the `--container-engine` flag.


### Parallel Builds

For efficient parallel builds of multiple targets, use the `-j ${number_of_threads}` option in the build script. However, note the following:

- Building in parallel significantly increases memory usage.
- There are no mechanisms in place to handle memory exhaustion gracefully.
- This feature is only recommended for users with large build machines, ideally with 8GiB of RAM per builder thread. It may work with 4GiB per thread due to spikes in memory usage being only intermittent during the build, but your milage may vary.

### Cross Architecture Builds

By default, the build targets the native architecture of the build system. However, cross-building for other architectures is simple.

Append the target architecture to the target name in the build command, like so: `./build ${target}-${arch}`.
For example, to build for both amd64 and arm64 architectures:

```
./build kvm-amd64 kvm-arm64
```

This requires setting up [binfmt_misc](https://docs.kernel.org/admin-guide/binfmt-misc.html) handlers for the target architecture, allowing the system to execute foreign binaries.

On most distributions, you can install QEMU user static to set up binfmt_misc handlers. For example, on Debian, use the command `apt install qemu-user-static`.

### SELinux

If you intend to build targets with the `_selinux` feature, some additional requirements apply to the build machine.


Building the `_selinux` feature will not work on machines running in SELinux enforcing mode. Ideally, you should build on a machine with SELinux disabled. However, if you want to build with SELinux in permissive mode, this can be achieved by running the build as root with the `--privileged` flag.

i.e.: `sudo ./build --privileged ${target}`

**SELinux Workaround for Podman:**
> :warning: **Note:** [Podman Desktop](https://podman-desktop.io) and [Podman on macOS](https://podman.io) have by default SELinux enabled in their VMs. This may cause issues when building the `_selinux` feature. See [issue #16](https://github.com/gardenlinux/builder/issues/16) for details.

If you're using Podman on macOS, follow these steps to disable SELinux in the podman VM:

1. SSH into the Podman VM: `podman machine ssh`
2. Run the following command to disable SELinux: `echo SELINUX=disabled | sudo tee /etc/selinux/config`
3. Exit the SSH connection.
4. Restart the Podman VM: `podman machine stop && podman machine start`

### Secureboot

If you intend to build targets with the `_secureboot` feature, you must first build the secureboot certificates.
Run the command `./cert/build` to generate the secureboot certificates.

By default, the command uses local files as the private key storage. However, you can configure it to use the AWS KMS key store by using the `--kms` flag. Note that valid AWS credentials need to be configured using the standard AWS environment variables.

## Troubleshooting

If you encounter any issues during the build process, refer to the [Garden Linux builder's troubleshooting section](https://github.com/gardenlinux/builder#troubleshooting) for guidance.

