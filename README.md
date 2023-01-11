[![build](https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml/badge.svg?event=schedule)](https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml)
[![build](https://github.com/gardenlinux/gardenlinux/actions/workflows/dev.yml/badge.svg?branch=main)](https://github.com/gardenlinux/gardenlinux/actions/workflows/dev.yml)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/3925/badge)](https://bestpractices.coreinfrastructure.org/projects/3925)
 [![MIT License](https://img.shields.io/github/license/gardenlinux/gardenlinux)](https://img.shields.io/github/license/gardenlinux/gardenlinux)
[![Gitter](https://badges.gitter.im/gardenlinux/community.svg)](https://gitter.im/gardenlinux/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![GitHub Open Issues](https://img.shields.io/github/issues-raw/gardenlinux/gardenlinux)](https://img.shields.io/github/issues-raw/gardenlinux/gardenlinux)
[![GitHub Closed PRs](https://img.shields.io/github/issues-pr-closed-raw/gardenlinux/gardenlinux)](https://img.shields.io/github/issues-pr-closed-raw/gardenlinux/gardenlinux)


# Garden Linux

<website-main>

<img align="left" width="80" height="80" src="https://raw.githubusercontent.com/gardenlinux/gardenlinux/main/logo/gardenlinux-logo-black-text.svg"> <a href="https://gardenlinux.io/">Garden Linux</a> is a <a href="https://debian.org/">Debian GNU/Linux</a> derivate that aims to provide small, auditable Linux images for most cloud providers (e.g. AWS, Azure, GCP etc.) and bare-metal machines. Garden Linux is the best Linux for <a href="https://gardener.cloud/">Gardener</a> nodes. Garden Linux provides great possibilities for customizing that is made by a highly customizable feature set to fit your needs. <br><br>

</website-main>

## Table of Content
- [Garden Linux](#garden-linux)
  - [Table of Content](#table-of-content)
  - [Features](#features)
  - [Quick Start](#quick-start)
    - [Build Requirements](#build-requirements)
    - [Build Options](#build-options)
    - [Building](#building)
    - [Cross-Build Support](#cross-build-support)
  - [Customizing](#customizing)
  - [Deploying](#deploying)
  - [Release](#release)
  - [Documentation](#documentation)
    - [Continous Integration](#continous-integration)
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

## Quick Start
The entire build runs in a <i>privileged</i> Podman/Docker container that orchestrates all further actions. If not explicitly skipped, unit tests will be performed. Extended capabilities are at least needed for loop back support. Currently `AMD64` and `ARM64` architectures are supported. Garden Linux can also be built in an *air-gapped* environment (offline) without any further internet connectivity. However, this requires to obtain all needed dependencies before. Further instructions can be found [here](https://github.com/gardenlinux/gardenlinux/tree/main/docs/build#build-in-an-air-gapped-environment).

By default, Garden Linux uses [Podman](https://podman.io/) as container runtime (`Docker` is optionally supported) for building Garden Linux images (Garden Linux artifacts however will have Docker in them to maintain compatibility with older Kubernetes versions). If - for whatever reason - you want or need to use Docker instead, you can set the environment variable `GARDENLINUX_BUILD_CRE=docker` before invoking the build.

### Build Requirements

**System:**
* RAM: 2+ GiB (use '--lessram' to lower memory usage)
* Disk: 10+ GiB (20+ GiB for running `integration tests`)
* Internet connection

**Packages:**

**Debian/Ubuntu:**

> mandatory:
> ```
> apt install --no-install-recommends bash sudo podman make 
> ```
> for release builds:
> ```
> apt install --no-install-recommends gnupg git 
> ```
> for platform tests:
> ```
> apt install --no-install-recommends qemu-system-x86 qemu-system-aarch64
> ```

**CentOS/RedHat (>=8):**

> CFSSL requires `GLIBC 2.28`. Therefore, we recommand to build on systems running CentOS/RedHat 8 or later.
>
> ```
> # Install needed packages
> yum install bash sudo podman crun make gnupg git qemu-kvm qemu-img coreutils edk2-aarch64 edk2-ovmf
> ```
> *Note: Running `AARCH64` on `x86_64` requires `qemu-system-aarch64` package which is not present in official repositories.*

**ArchLinux/Manjaro:**
> ```
> pacman -S bash sudo podman crun make coreutils gnupg git qemu-system-x86 qemu-system-aarch64 edk2-ovmf
> ```

**macOS (>=12):**

> Build support on `macOS` (>=12) supports `Intel` (AMD64) and `Apple Silicon` (ARM64/AARCH64) architectures. Building on macOS requires the GNU versions of multiple tools that can be installed in different ways like Brew, MacPorts or self compiled. Self compiled GNU packages must be located in `/opt/local/bin/`. However, the following build instructions only cover the recommended `Brew` way.
>
> Furthermore, building on macOS requires to fulfill further build requirements:
> * Command Line Tools (CLT) for Xcode
> * [Homebrew](https://brew.sh) (Optionally: MacPorts https://macports.org)
> * [Docker](https://docs.docker.com/desktop/mac/install/)
>
> ```
> # Install needed packages
> brew install coreutils bash gnu-getopt gnu-sed gawk podman socat
>
> # Change to bash (Default: ZSH)
> bash
>
> # Export Docker as Container Runtime Environment for Garden Linux
> export GARDENLINUX_BUILD_CRE=docker
> ```

**Adjust Repository:**

*Note: This is **not** needed on macOS.*

Add `docker.io` to `unqualified-search-registries` in your [registries.conf](https://github.com/containers/image/blob/main/docs/containers-registries.conf.5.md). On freshly installed `Podman` systems this can be done by executing:
```
echo 'unqualified-search-registries = ["docker.io"]' | sudo tee -a /etc/containers/registries.conf
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
| --debian-mirror | Adds the native Debian repository (default: off [*only for development available*]) |
| --tests | Test suite to use, available tests are unittests, kvm, chroot (default: unittests) |
| --skip-build | Do not create the build container |

### Building
To build all supported images you may just run the following command:
```
    make all
```

However, to save time you may also build just a platform specific image by running one of the following commands. Related dev images can be created by appending the '_dev' suffix (e.g. "make aws_dev").
```
    make ali
    make aws
    make azure
    make container
    make firecracker
    make gcp
    make kvm
    make metal
    make openstack
    make vmware
```

You may also generate a list of all default targets by running:
```
make generate-targets
```
Afterwards, all targets are located within the `make_targets.cache` file in the project's root directory.

After building, all artifacts are located in the `.build/` folder of the project's root directory.

### Cross-Build Support
The Garden Linux pipeline supports cross-building on Linux based systems and requires `binfmt` support. `binfmt` support can easily be installed via packages from the used distribution. Afterwards, the build option `--arch` must be defined to the target arch (e.g. `--arch arm64`). Currently, `amd64` and `arm64` are supported and must be explicitly defined for cross-building.

**Package Installation**

**Debian:**
```
apt-get install binfmt-support
```

**CentOS:**
```
yum install qemu-user-binfmt
```
**ArchLinux/Manjaro:**
```
yay -S binfmt-qemu-static-all-arch
```

**macOS:**

Not supported.


## Customizing
Building Garden Linux is based on a [feature system](features/README.md).

| Feature Type | Includes |
|---|---|
| Platforms | `ali`, `aws`, `azure`, `gcp`, `kvm`, `metal`, ... |
| Features | `container host`, `vitual host`, ... |
| Modifiers | `_slim`, `_readonly`, `_pxe`, `_iso`, ... |
| Element | `cis`, `fedramp`, `gardener` |

if you want to build manually choose:
```
build.sh  --features <Platform>,[<feature1>],[<featureX>],[_modifier1],[_modifierX] destination [version]
```

Additionally, please find some `build.sh` example calls in the `Makefile`.

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

Link: <a href="https://gitter.im/gardenlinux/community">https://gitter.im/gardenlinux/community</a>
