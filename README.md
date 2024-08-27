<p style="text-align: center;">
    <img alt="GitHub Release" src="https://img.shields.io/github/v/release/gardenlinux/gardenlinux?label=LTS%20release">
    <a href="https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml" target="_blank">
        <img src="https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml/badge.svg?event=schedule" alt="Build">
    </a>
    <a href="https://github.com/gardenlinux/gardenlinux/actions/workflows/dev.yml" target="_blank">
        <img src="https://github.com/gardenlinux/gardenlinux/actions/workflows/dev.yml/badge.svg?branch=main" alt="Build">
    </a>
    <a href="https://bestpractices.coreinfrastructure.org/projects/3925" target="_blank">
        <img src="https://bestpractices.coreinfrastructure.org/projects/3925/badge" alt="CII Best Practices">
    </a>
  </p>
</p>

# Garden Linux

<website-main>

<img align="left" width="80" height="80" src="https://raw.githubusercontent.com/gardenlinux/gardenlinux/main/logo/gardenlinux-logo-black-text.svg"> <a href="https://gardenlinux.io/">Garden Linux</a> is a <a href="https://debian.org/">Debian GNU/Linux</a> derivate that aims to provide small, auditable Linux images for most cloud providers (e.g. AWS, Azure, GCP etc.) and bare-metal machines. Garden Linux is the best Linux for <a href="https://gardener.cloud/">Gardener</a> nodes. Garden Linux provides great possibilities for customizing that is made by a highly customizable feature set to fit your needs. <br><br>

</website-main>


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
  - Platform tests (Image platform tests in all supported platforms)
  - License violations (Testing for any license violations)
  - Outdated software versions (Testing for outdated software)
- Supporting major platforms out-of-the-box
  - Major cloud providers AWS, Azure, Google, Alicloud
  - Major virtualizer VMware, OpenStack, KVM
  - Bare-metal systems

# Build

The build system utilises the [gardenlinux/builder](https://github.com/gardenlinux/builder) to create customized Linux distributions.
[gardenlinux/gardenlinux](https://github.com/gardenlinux/gardenlinux) is maintained by the Garden Linux team, highlighting specialized "features" available for other projects.

> [!TIP]
> For further information about the build process, and how to set it up on your machine, refer to [the _Build Image_ documentation page](docs/01_developers/build_image.md).

To initiate a build, use the command:
```shell
./build ${platform}-${feature}_${modifier}
```

Where:
- `${platform}` denotes the desired platform (e.g., `kvm`, `metal`, `aws`).
- `${feature}` represents a specific feature from the `features/` folder.
- `${modifier}` is an optional modifier from the `features/` folder, prefixed with an underscore "_".

You can combine multiple platforms, features, and modifiers as needed.

Example:
```shell
./build kvm-python_dev
```

The build script fetches the required builder container and manages all internal build steps. By default, it uses rootless podman, but you can switch to another container engine with the `--container-engine` flag.

# Test

To run unit tests for a specific target, use the command `./test ${target}`.
Further documentation about tests is located in [tests/README.md](tests/README.md).


# Download Releases 

| Product                        | Release Frequency | Download                                                                                        |
| ------------------------------ | ----------------- | ----------------------------------------------------------------------------------------------- |
| LTS cloud and baremetal images | Quarterly         | [Download](https://github.com/gardenlinux/gardenlinux/releases)                                 |
| LTS base container images      | Quarterly         | [Download](https://github.com/gardenlinux/gardenlinux/pkgs/container/gardenlinux)               |
| LTS bare python container      | Quarterly         | [Download](https://github.com/gardenlinux/gardenlinux/pkgs/container/gardenlinux%2Fbare-python) |
| LTS bare libc container        | Quarterly         | [Download](https://github.com/gardenlinux/gardenlinux/pkgs/container/gardenlinux%2Fbare-libc)   |
| LTS bare nodejs container      | Quarterly         | [Download](https://github.com/gardenlinux/gardenlinux/pkgs/container/gardenlinux%2Fbare-nodejs) |

**Note:** For each artifact, there also exists a nightly version, which is built daily but is not considered LTS.

The LTS cloud and baremetal images provided by Garden Linux are compatible with various cloud platforms, including Alibaba Cloud, AWS, Microsoft Azure and GCP.

# Nvidia Driver Support
An installer can be found in the [gardenlinux/gardenlinux-nvidia-installer](https://github.com/gardenlinux/gardenlinux-nvidia-installer) repository.

# Documentation
Please refer to [docs/README.md](https://github.com/gardenlinux/gardenlinux/tree/main/docs#readme).

# Contributing

Contributions to the Garden Linux open source projects are welcome. 
More information are available in in <a href="CONTRIBUTING.md">CONTRIBUTING.md</a> and our `docs/`.

# Community
If you need further assistance, have any issues or just want to get in touch with other Garden Linux users feel free to join our public chat room on Gitter.

Link: <a href="https://gitter.im/gardenlinux/community">https://gitter.im/gardenlinux/community</a>
