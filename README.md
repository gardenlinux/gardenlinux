[![build](https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml/badge.svg?event=schedule)](https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml)
[![build](https://github.com/gardenlinux/gardenlinux/actions/workflows/dev.yml/badge.svg?branch=main)](https://github.com/gardenlinux/gardenlinux/actions/workflows/dev.yml)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/3925/badge)](https://bestpractices.coreinfrastructure.org/projects/3925)
 [![MIT License](https://img.shields.io/github/license/gardenlinux/gardenlinux)](https://img.shields.io/github/license/gardenlinux/gardenlinux)
[![Gitter](https://badges.gitter.im/gardenlinux/community.svg)](https://gitter.im/gardenlinux/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![GitHub Open Issues](https://img.shields.io/github/issues-raw/gardenlinux/gardenlinux)](https://img.shields.io/github/issues-raw/gardenlinux/gardenlinux)
[![GitHub Closed PRs](https://img.shields.io/github/issues-pr-closed-raw/gardenlinux/gardenlinux)](https://img.shields.io/github/issues-pr-closed-raw/gardenlinux/gardenlinux)
[![GitLab Package Check](https://github.com/gardenlinux/gardenlinux/actions/workflows/check-packages.yml/badge.svg)](https://github.com/gardenlinux/gardenlinux/actions/workflows/check-packages.yml)


# Garden Linux

<website-main>

<img align="left" width="80" height="80" src="https://raw.githubusercontent.com/gardenlinux/gardenlinux/main/logo/gardenlinux-logo-black-text.svg"> <a href="https://gardenlinux.io/">Garden Linux</a> is a <a href="https://debian.org/">Debian GNU/Linux</a> derivate that aims to provide small, auditable Linux images for most cloud providers (e.g. AWS, Azure, GCP etc.) and bare-metal machines. Garden Linux is the best Linux for <a href="https://gardener.cloud/">Gardener</a> nodes. Garden Linux provides great possibilities for customizing that is made by a highly customizable feature set to fit your needs. <br><br>

</website-main>

## Table of Contents
- [Garden Linux](#garden-linux)
- [Features](#features)
- [Build](#build)
  - [Build Requirements](#build-requirements)
  - [Parallel Builds](#parallel-builds)
  - [Cross Architecture Builds](#cross-architecture-builds)
  - [SELinux](#selinux)
  - [Secureboot](#secureboot)
  - [Maintained Images](#maintained-images)
- [Building 934](#building-934)
- [Tests](#tests)
- [Deploying](#deploying)
- [Release](#release)
- [Documentation](#documentation)
  - [Continuous Integration](#continuous-integration)
  - [Integration Tests](#integration-tests)
- [Contributing](#contributing)
- [Community](#community)

## Features
- Easy to use build system
- Repeatable and auditable builds
- Small footprint
- Purely systemd based (network, fstab etc.)
- Initramfs is dracut generated
- Running latest LTS Kernel
- [MIT](https://github.com/gardenlinux/gardenlinux/blob/master/LICENSE.md) license
- Security
  - Fully immutable image(s) *(optional)*
  - OpenSSL 3.0 *(default)*
  - CIS Framework *(optional)*
- Testing
  - Unit tests (Created image testing)
  - Integration tests (Image integration tests in all supported platforms)
  - License violations (Testing for any license violations)
  - Outdated software versions (Testing for outdated software)
- Supporting major platforms out-of-the-box
  - Major cloud providers AWS, Azure, Google, Alicloud
  - Major virtualizer VMware, OpenStack, KVM
  - Bare-metal systems

## Build

The build system utilises the [gardenlinux/builder](https://github.com/gardenlinux/builder) to create customized Linux distributions. [gardenlinux/gardenlinux](https://github.com/gardenlinux/gardenlinux) is maintained by the Garden Linux team, highlighting specialized "features" available for other projects.



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


### Build Requirements

- **Memory:** The build process may require up to 8GiB of memory, depending on the selected targets. If your system has insufficient RAM, configure swap space accordingly.
- **Container Engine:** The Builder has minimal dependencies and only requires a working container engine. You have two options:
  - **Rootless Podman:** It's recommended to use rootless Podman. Please refer to the [Podman rootless setup guide](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md) for instructions on setting it up.
  - **Sudo Podman:** Alternatively, you can use Podman with sudo for elevated privileges.

To ensure a successful build, please refer to the [Build Requirements section](https://github.com/gardenlinux/builder#requirements) in the `gardenlinux/builder` repository.

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

### Maintained Images

Garden Linux offers a range of official images tailored for various architectures and platforms. Instead of listing all the specific image variants here, you can find the most up-to-date list of maintained images on the [Garden Linux releases page on GitHub](https://github.com/gardenlinux/gardenlinux/releases).

**Supported Architectures:**
- arm64
- amd64

**Supported Platforms:**


| Name | Identifier |
|------|------------|
| [Ali](https://github.com/gardenlinux/gardenlinux/tree/main/features/ali) | `ali` |
| [AWS](https://github.com/gardenlinux/gardenlinux/tree/main/features/aws) | `aws` |
| [Azure](https://github.com/gardenlinux/gardenlinux/tree/main/features/azure) | `azure` |
| [GCP](https://github.com/gardenlinux/gardenlinux/tree/main/features/gcp) | `gcp` |
| [KVM](https://github.com/gardenlinux/gardenlinux/tree/main/features/kvm) | `kvm` |
| [Metal](https://github.com/gardenlinux/gardenlinux/tree/main/features/metal) | `metal` |
| [OpenStack](https://github.com/gardenlinux/gardenlinux/tree/main/features/openstack) | `openstack` |
| [VMware](https://github.com/gardenlinux/gardenlinux/tree/main/features/vmware) | `vmware` |


To understand the build process for these images, refer to the [build action](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/build.yml). For details on the publishing process, check out the [upload action](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/upload_to_s3.yml) and the [gardenlinux/glci](https://github.com/gardenlinux/glci) repository.

## Building 934

For the sake of reproducibility, the earlier versions like 934 use the old Garden Linux builder.

Here's a quick guide on building the 934 image:
```shell
git checkout rel-934
# Ensure you're working in a clean environment (optional but recommended)
make clean
make aws-prod
```

If you encounter any issues specifically with the 934 build, please [open an issue](https://github.com/gardenlinux/gardenlinux/issues) on our GitHub repository. Make sure to mention that your issue pertains to the 934 build for clarity.

## Tests

To run unit tests for a specific target, use the command `./test ${target}`.

## Deploying
Deploying on common cloud platforms requires additional packages. The following overview gives a short quick start to run cloud platform deployments. Currently, all modules are based on `Python`. Therefore, please make sure to have Python installed.

| Platform | Module  |
|---|---|
| Alicloud | [Aliyun CLI](https://github.com/aliyun/aliyun-cli)
| AWS | [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
| Azure | [Azure CLI](https://docs.microsoft.com/de-de/cli/azure/install-azure-cli-apt)
| GCP | [Cloud SDK](https://cloud.google.com/sdk/docs/quickstart?utm_source=youtube&utm_medium=Unpaidsocial&utm_campaign=car-20200311-Quickstart-Mac#linux), [gsutil](https://cloud.google.com/storage/docs/gsutil_install?hl=de#install)
| OpenStack | [OpenStackCLI](https://github.com/openstack/python-openstackclient)

## Release
Garden Linux frequently publishes snapshot releases. These are available as machine images in most major cloud providers as well as file-system images for manual import. See the [releases](https://github.com/gardenlinux/gardenlinux/releases) page for more info.

## Documentation
Garden Linux provides a great documentation for build options, customizing, configuration, tests and pipeline integrations. The documentation can be found within the project's `docs/` path or by clicking <a href="https://github.com/gardenlinux/gardenlinux/tree/main/docs">here</a>. Next to this, you may find a corresponding `README.md` in each directory explaining some more details. Below, you may find some important documentations for continuous integration and integration tests.

### Continuous Integration
Garden Linux can build in an automated way for continuous integration. See [.github/workflows/README.md](.github/workflows/README.md) for details.

### Integration Tests
While it may be confusing for beginners we highlight this chapter for `integration tests` here. Garden Linux supports integration testing on all major cloud platforms (Alicloud, AWS, Azure, GCP). To allow testing even without access to any cloud platform we created an universal `kvm` platform that may run locally and is accessed in the same way via a `ssh client object` as any other cloud platform. Therefore, you do not need to adjust tests to perform local integration tests. Just to mention here that there is another platform called `chroot`. This platform is used to perform `unit tests` and will run as a local `integration test`. More details can be found within the documentation in  [tests/README.md](tests/README.md).

## Contributing

Feel free to add further documentation, to adjust already existing one or to contribute with code.
Please take care about our style guide and naming conventions.
More information are available in in <a href="CONTRIBUTING.md">CONTRIBUTING.md</a> and our `docs/`.
Be aware that this repository leverages the [gardenlinux/builder](https://github.com/gardenlinux/builder) for creating customized Linux distributions. While `gardenlinux/gardenlinux` is a representation of one such distribution.

## Community
Garden Linux has a large grown community. If you need further assistance, have any issues or just want to get in touch with other Garden Linux users feel free to join our public chat room on Gitter.

Link: <a href="https://gitter.im/gardenlinux/community">https://gitter.im/gardenlinux/community</a>
