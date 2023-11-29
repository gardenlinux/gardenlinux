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

Garden Linux is a versatile and secure Debian-based Linux distribution, offering:

- An intuitive and repeatable build system.
- Efficient performance with a small system footprint.
- Strong security features including optional immutable images and latest security standards.
- Extensive testing to ensure reliability and compliance.
- Broad support for major cloud providers, virtualization platforms, and bare-metal installations.

For a complete list of features and detailed use-case descriptions, please see our [Full Feature Matrix](https://github.com/gardenlinux/gardenlinux/tree/main/docs/00_introduction/features.md).


## Quickstart
```
./build metal # Build Garden Linux metal flavor
./test metal # Test Garden Linux metal flavor
```

## Build
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

Further information on how to build Garden Linux can be found [here](https://github.com/gardenlinux/gardenlinux/tree/main/docs/01_developers/build_image.md).

## Full Documentation

For detailed information on Garden Linux click [here](https://github.com/gardenlinux/gardenlinux/tree/main/docs). 
📚 This resource covers everything from introduction to advanced configurations.

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

## Tests

To run local tests for a specific target, use the command `./test ${target}`.

### Platform Tests
Garden Linux supports platform tests for all major cloud platforms (Alicloud, AWS, Azure, GCP). To allow testing even without access to any cloud platform we created an universal `kvm` platform that may run locally and is accessed in the same way via a `ssh client object` as any other cloud platform. Therefore, you do not need to adjust tests to perform  tests locally. This platform is used to perform `unit tests` and will run as a local `integration test`. More details can be found within the documentation in  [tests/README.md](tests/README.md).


## Contributing

Feel free to add further documentation, to adjust already existing one or to contribute with code.
Please take care about our style guide and naming conventions.
More information are available in in <a href="CONTRIBUTING.md">CONTRIBUTING.md</a> and our `docs/`.
Be aware that this repository leverages the [gardenlinux/builder](https://github.com/gardenlinux/builder) for creating customized Linux distributions. While `gardenlinux/gardenlinux` is a representation of one such distribution.

## Community
Garden Linux has a large grown community. If you need further assistance, have any issues or just want to get in touch with other Garden Linux users feel free to join our public chat room on Gitter.

Link: <a href="https://gitter.im/gardenlinux/community">https://gitter.im/gardenlinux/community</a>
