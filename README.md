[![build](https://github.com/gardenlinux/gardenlinux/actions/workflows/build.yml/badge.svg)](https://github.com/gardenlinux/gardenlinux/actions/workflows/build.yml)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/3925/badge)](https://bestpractices.coreinfrastructure.org/projects/3925)
 [![MIT License](https://img.shields.io/github/license/gardenlinux/gardenlinux)](https://img.shields.io/github/license/gardenlinux/gardenlinux)
[![Gitter](https://badges.gitter.im/gardenlinux/community.svg)](https://gitter.im/gardenlinux/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![GitHub Open Issues](https://img.shields.io/github/issues-raw/gardenlinux/gardenlinux)](https://img.shields.io/github/issues-raw/gardenlinux/gardenlinux)
[![GitHub Closed PRs](https://img.shields.io/github/issues-pr-closed-raw/gardenlinux/gardenlinux)](https://img.shields.io/github/issues-pr-closed-raw/gardenlinux/gardenlinux)


# Garden Linux
<img align="left" width="80" height="80" src="https://raw.githubusercontent.com/gardenlinux/gardenlinux/main/logo/gardenlinux-logo-black-text.svg"> <a href="https://gardenlinux.io/">Garden Linux</a> is a <a href="https://debian.org/">Debian GNU/Linux</a> derivate that aims to provide small, auditable linux images for most Cloud Providers (e.g. AWS, Azure, GCP etc.) and Bare Metal. Garden Linux is the best Linux for <a href="https://gardener.cloud/">Gardener</a> nodes. Garden Linux provides great possibilities for customizing and provides a great feature set to fit your needs. <br><br>

## Table of Content
- [Features](#Features)
- [Quick Start](#Quick-Start)
  * [Build Requirements](#Build-Requirements)
  * [Build Options](#Build-Options)
  * [Building](#Building)
- [Customizing](#Customizing)
- [Release](#Release)
- [Documentation](#Documentation)
  * [Continous Integration](#Continous-Integration)
  * [Integration Tests / Unit Tests](#Integration-Tests)
- [Contributing](#Contributing)
- [Community](#Community)

## Features
- Easy to use build system
- Builds are repeatable and auditable
- Small footprint
- Purely systemd based (network, fstab etc.)
- Initramfs is dracut generated
- Optional complete immutability
- Thorough automated testing
  - Unit tests against the local build
  - Integration tests against the supported cloud platforms
  - License violations
  - Outdated software versions
- Aiming to always integrate the latest LTS Kernel
- Project licensed under [MIT](https://github.com/gardenlinux/gardenlinux/blob/master/LICENSE.md)
- Supporting major platforms out-of-the-box
  - Major cloud providers AWS, Azure, Google, Alicloud
  - Major virtualizer VMware, OpenStack, KVM
  - Bare Metal

## Quick Start
The entire build runs in a <i>privileged</i> Podman/Docker container that orchestrates all further actions. If not explicitly skipped, unit tests will be performed. Extended capabilities are at least needed for loop back support. Currently AMD64 and ARM64 architectures are supported.

By default, Garden Linux uses [Podman](https://podman.io/) as container runtime for building Garden Linux images (Garden Linux artifacts however will have Docker in them to maintain compatibility with older Kubernetes versions). If - for whatever reason - you want or need to use Docker instead, you can set the environment variable `GARDENLINUX_BUILD_CRE=docker` before invoking the build.

### Build Requirements

**System:**
* RAM: 2+ GiB (use '--lessram' to lower memory usage)
* Disk: 10+ GiB
* Internet connection

**Packages:**

**Debian/Ubuntu:**
```
apt install bash podman crun make coreutils gnupg git qemu-system-x86 qemu-system-aarch64
```

**CentOS/RedHat (>=8):**

CFSSL requires `GLIBC 2.28`. Therefore, we recommand to build on systems running CentOS/RedHat 8 or later.

```
# Install needed packages
yum install bash podman crun make gnupg git qemu-kvm qemu-img
```

**Adjust Repository:**

Add `docker.io` to `unqualified-search-registries` in your [registries.conf](https://github.com/containers/image/blob/main/docs/containers-registries.conf.5.md). On freshly installed `Podman` systems this can be done by executing:
```
echo 'unqualified-search-registries = ["docker.io"]' >> /etc/containers/registries.conf
```
If `Podman` was already present please add the repository yourself to `unqualified-search-registries` in `/etc/containers/registries.conf`.

**Kernel Modules:**
* ext4
* loop
* squashfs
* vfat
* vsock <i><small>(image builds and extended virtualized tests)</i></small>

### Build Options
| Option | Description  |
|---|---|
| --features  | Comma separated list of features activated (see features/) (default:base) |
| --disable-features | Comma separated list of features to deactivate (see features/) |
| --lessram | Build will be no longer in memory (default: off) |
| --debug | Activates basically \`set -x\` everywhere (default: off) |
| --manual | Built will stop in build environment and activate manual mode (default:off) |
| --arch | Builds for a specific architecture (default: architecture the build runs on) |
| --suite | Specifies the debian suite to build for e.g. bullseye, potatoe (default: testing) |
| --skip-tests | Deactivating tests (default: off) |
| --tests | Test suite to use, available tests are unittests, kvm, chroot (default: unittests) |
| --skip-build | Do not create the build container |

### Building

To build all supported images you may just run the following command:
```
    make all
```

However, to save time you may also build just a platform specific image by running one of the following commands. Related dev images can be created by appending the '-dev' suffix (e.g. "make aws-dev").
```
    make aws
    make gcp
    make azure
    make ali
    make vmware
    make openstack
    make kvm
    make metal
```

Artifacts are located in the `.build/` folder of the project's build directory.

## Customizing
Building Garden Linux is based on a [feature system](features/README.md).

| Feature Type | Includes |
|---|---|
| Platforms | ali, aws, azure, gcp, kvm, baremetal... |
| Features | container host, vitual host, ... |
| Modifiers | _slim, _readonly, _pxe, _iso ... |
| Element | cis, fedramp, gardener |

if you want to build manually choose:
```
build.sh  --features <Platform>,[<feature1>],[<featureX>],[_modifier1],[_modifierX] destination [version]
```
**Example:**
```
build.sh  --features server,cloud,cis,vmware .build/
```
This builds a server image, cloud-like, with `CIS`feature for the VMware platform. The build result can be found in `.build/`. Also look into our [Version scheme](VERSION.md) since adding a date or a Version targets the whole build for a specific date.

## Deploying
Deploying on common cloud platforms requires additional packages. The following overview gives a short quick start to run cloud platform deployments. Currently, all modules are based on `Python`. Therefore, please make sure to have Python installed.

| Platform | Module  |
|---|---|
| Alicloud | [Aliyun CLI](https://github.com/aliyun/aliyun-cli)
| AWS: | [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
| Azure | [Azure CLI](https://docs.microsoft.com/de-de/cli/azure/install-azure-cli-apt)
| GCP: | [Cloud SDK](https://cloud.google.com/sdk/docs/quickstart?utm_source=youtube&utm_medium=Unpaidsocial&utm_campaign=car-20200311-Quickstart-Mac#linux), [gsutil](https://cloud.google.com/storage/docs/gsutil_install?hl=de#install)
| OpenStack | [OpenStackCLI](https://github.com/openstack/python-openstackclient)

## Release
Garden Linux frequently publishes snapshot releases. These are available as machine images in most major cloud providers as well as file-system images for manual import. See the [releases](https://github.com/gardenlinux/gardenlinux/releases) page for more info.

## Documentation
Garden Linux provides a great documentation for build options, customizing, configuration, tests and pipeline integrations. The documentation can be found within the project's `docs/` path or by clicking <a href="https://github.com/gardenlinux/gardenlinux/tree/main/docs">here</a>. Next to this, you may find a corresponding `README.md` in each directory explaning some more details. Below, you may find some important documentations for continous integration and integration tests.

### Continous Integration
Garden Linux can build in an automated way for continous integration. See [ci/README.md](ci/README.md) for details.

### Integration Tests
While it may be confusing for beginners we highlight this chapter for `integration tests` here. Garden Linux supports integration testing on all major cloud platforms (Alicloud, AWS, Azur, GCP). To allow testing even without access to any cloud platform we created an universal `kvm` platform that may run locally and is accessed in the same way via a `ssh client object` as any other cloud platform. Therefore, you do not need to adjust tests to perform local integration tests. Just to mention here that there is another platform called `chroot`. This platform is used to perform `unit tests` and will run as a local `integration test`. More details can be found within the documentation in  [tests/README.md](tests/README.md).

## Contributing
Feel free to add further documentation, to adjust already existing one or to contribute with code. Please take care about our style guide and naming conventions. More information are available in in <a href="CONTRIBUTING.md">CONTRIBUTING.md</a> and our `docs/`.

## Community
Garden Linux has a large grown community. If you need further asstiance, have any issues or just want to get in touch with other Garden Linux users feel free to join our public chat room on Gitter.

Link: https://gitter.im/gardenlinux/community
