# Garden Linux Tests Next Generation (tests-ng)

This directory contains the next generation testing framework for Garden Linux images. The framework supports testing Garden Linux images in various environments including chroot, QEMU virtual machines, and cloud providers.

## Table of Contents

- [Garden Linux Tests Next Generation (tests-ng)](#garden-linux-tests-next-generation-tests-ng)
  - [Table of Contents](#table-of-contents)
  - [Structure](#structure)
  - [Running Tests](#running-tests)
    - [Prerequisites](#prerequisites)
      - [Install on Debian based systems](#install-on-debian-based-systems)
      - [Install on MacOS](#install-on-macos)
    - [Basic Usage](#basic-usage)
    - [Command Line Flags](#command-line-flags)
      - [Common Options](#common-options)
      - [Cloud Specific Options](#cloud-specific-options)
      - [QEMU Specific Options](#qemu-specific-options)
    - [Examples](#examples)
    - [Cloud Provider Authentication and Configuration](#cloud-provider-authentication-and-configuration)
      - [ALI](#ali)
      - [AWS](#aws)
      - [Azure](#azure)
      - [GCP](#gcp)
      - [Openstack](#openstack)
  - [Debugging Tests](#debugging-tests)
    - [Login Scripts](#login-scripts)
      - [QEMU Environment](#qemu-environment)
        - [Debug Tests in QEMU using VS Code](#debug-tests-in-qemu-using-vs-code)
      - [Cloud Environment](#cloud-environment)
  - [Test Environment Details](#test-environment-details)
    - [Chroot Testing](#chroot-testing)
    - [QEMU Testing](#qemu-testing)
    - [Cloud Testing](#cloud-testing)
  - [Test Distribution Build Process](#test-distribution-build-process)
    - [Build Components](#build-components)
    - [Build Process](#build-process)
    - [Automatic Building](#automatic-building)
    - [Test Distribution Structure](#test-distribution-structure)
  - [Test Development](#test-development)
    - [Markers](#markers)

## Structure

```
tests-ng/
├── util/                   # Utility scripts for running tests
│   ├── run.sh              # Main entry point for running tests
│   ├── run_chroot.sh       # Chroot testing environment
│   ├── run_qemu.sh         # QEMU VM testing environment
│   ├── run_cloud.sh        # Cloud provider testing
│   ├── login_qemu.sh       # SSH login to QEMU VM
│   ├── login_cloud.sh      # SSH login to cloud VM
│   └── tf/                 # Terraform configurations for cloud
├── plugins/                # Test plugins and utilities
│   └── ...
└── test_*.py               # Individual tests
```

## Running Tests

### Prerequisites

Before running the test framework, make sure the following dependencies are installed:

- `podman`
- `make`
- `curl`
- `jq`
- `unzip`
- `qemu`
- `qemu-utils`

#### Install on Debian based systems

```
apt-get update
apt-get install podman make curl jq unzip qemu swtpm

```

#### Install on MacOS

```
brew install coreutils bash gnu-sed gnu-getopt podman make curl jq unzip swtpm
```

### Basic Usage

The main entry point is `./test-ng` in the gardenlinux root directory (symlink to )`tests-ng/util/run.sh`). It automatically detects the image type and runs appropriate tests:

> [!TIP]
> Use `./test-ng --help` to see all available options and examples.

```bash
# For chroot testing (tar files)
./test-ng .build/$image.tar

# For QEMU VM testing (raw files)
./test-ng .build/$image.raw

# For cloud provider testing (raw files only)
./test-ng --cloud aws .build/$image.raw
./test-ng --cloud gcp .build/$image.raw
./test-ng --cloud azure .build/$image.raw
./test-ng --cloud ali .build/$image.raw
```

### Command Line Flags

#### Common Options

- `--help`: Show help message and exit.
- `--skip-cleanup`: Skip cleanup of cloud resources after testing.
  - QEMU VM: After running/skipping the tests, you can stop/cleanup the VM with `ctrl + c`.
  - cloud: To cleanup up cloud resources after passing the flag, just re-run without the flag or use `--only-cleanup`.
- `--skip-tests`: Skip running the actual test suite
- `--test-args`: Pass any commandline argument to `pytest`. Put multiple arguments inside `""`.

#### Cloud Specific Options

- `--cloud <provider>`: Specify cloud provider (aws, gcp, azure, ali).
  - QEMU VM: Ignores this flag.
- `--cloud-image`: Use an existing cloud image.
  - possible images are listed on official releases, e.g. [1592.12](https://github.com/gardenlinux/gardenlinux/releases/tag/1592.12)
    - ali: `m-d7o7skltl4qe9anmwdp4` (eu-west-1 amd64)
    - aws: `ami-0d8d06eb3a44ae794` (eu-central-1 amd64)
    - gcp: `gardenlinux-gcp-ff804026cbe7b5f2d6f729e4-1592-12-c6d7f9a9` (amd64)
    - azure: `/CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-gen2/Versions/1592.12.0` (amd64)
- `--only-cleanup` Only run `tofu destroy` for cloud setups.
- `--image-requirements-file` Only needed with `--cloud-image`. Needs to point to a valid `*.requirements` file.

#### QEMU Specific Options

- `--ssh`: Enable SSH access to QEMU VM (`gardenlinux@127.0.01:2222`).
  - cloud: SSHD is always enabled via `cloud-init`.
- `--debug`: Enable debug mode (display window) for QEMU VM.

### Examples

```bash
# Run chroot tests on a tar image
./test-ng .build/aws-gardener_prod-amd64-today-13371337.tar

# Run QEMU tests with SSH access and skip cleanup
./test-ng --ssh --skip-cleanup .build/aws-gardener_prod-amd64-today-13371337.raw

# Run cloud tests on AWS, skipping cleanup
./test-ng --cloud aws --skip-cleanup .build/aws-gardener_prod-amd64-today-13371337.raw

# Run cloud tests but skip the test execution and cleanup
./test-ng --cloud aws --skip-tests --skip-cleanup .build/aws-gardener_prod-amd64-today-13371337.raw

# Run QEMU tests and only run the test test_ssh.py in verbose mode
./test-ng --test-args "test_ssh.py -v" aws-gardener_prod-amd64-today-13371337.raw

# Run cloud tests skip cleanup and only run the tests test_ssh.py and test_aws.py in verbose mode
./test-ng --cloud aws --skip-cleanup --test-args "test_ssh.py test_aws.py -v" .build/aws-gardener_prod-amd64-today-13371337.raw

# Spin up an existing cloud image using image requirements file
./test-ng --cloud aws --skip-cleanup --skip-tests --cloud-image --image-requirements-file .build/aws-gardener_prod-amd64-today-local.requirements ami-07f977508ed36098e
```

### Cloud Provider Authentication and Configuration

Before running tests, you need to authenticate with the cloud providers you want to test against. Each provider has its own authentication method.

#### ALI

ALI reuqires you to set up an [AccessKey pair](https://www.alibabacloud.com/help/en/cli/configure-credentials#0da5d08f581wn):

```
# select profile
export ALIBABA_CLOUD_PROFILE=gardenlinux-test

# configure your existing ALI credentials (only needed once)
aliyun configure --profile $ALIBABA_CLOUD_PROFILE

# check access
aliyun sts GetCallerIdentity
```

#### AWS

AWS requires [IAM user credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-authentication-user.html):

```
# select profile
export AWS_PROFILE=gardenlinux-test

# configure your existing AWS credentials (only needed once)
aws configure

# check access
aws sts get-caller-identity
```

> [!NOTE]
> For AWS, you can also use SSO authentication if your organization supports it.

#### Azure

Azure requires [user authentication via Azure CLI](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli):

```
# configure your existing Azure Subscription
export ARM_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# login
az login

# check access
az account show
```

> [!NOTE]
> The subscription ID can be found in the Azure portal under Subscriptions.

#### GCP

GCP requires [user authentication via gcloud CLI](https://cloud.google.com/docs/authentication/gcloud):

```
# configure your existing Google Cloud Project
export GOOGLE_PROJECT="gardenlinux-test"

# configure your existing GCP credentials (only needed once)
gcloud config set project ${GOOGLE_PROJECT}

# login
gcloud auth application-default login

# check access
gcloud auth list
```

> [!NOTE]
> The Project ID can be found in the Google Cloud portal under Project info.

#### Openstack

```
# download or configure ~/.config/openstack/clouds.yaml
# select profile
export OS_CLOUD=gardenlinux-test
```

> [!NOTE]
> You can download the `clouds.yaml` from your OpenStack dashboard.

## Debugging Tests

### Login Scripts

#### QEMU Environment

To connect to a running QEMU VM:

```bash
# Get a SSH Session
./util/login_qemu.sh

# Get a SSH Session with custom user
./util/login_qemu.sh --user admin

# Execute a command directly
./util/login_qemu.sh "uname -a"

# Run tests manually after login
cd /run/gardenlinux-tests && ./run_tests --system-booted --allow-system-modifications --expected-users gardenlinux
```

**Note**: Login to QEMU VMs (on a second shell) is only possible if `--ssh --skip-cleanup` is passed. SSHD is reachable on `127.0.0.1:2222` with the user `gardenlinux`. The QEMU VM will stay open in the shell that started and can be stopped with `ctrl + c`.


##### Debug Tests in QEMU using VS Code

1. Start the vm as described in the previous section

2. Configure the ssh connection for example by adding this block to `~/.ssh/config` (be sure to check if any parameter needs to be changed)

```
Host gardenlinux-qemu
    HostName 127.0.0.1
    Port 2222
    User gardenlinux
    IdentityFile ~/.ssh/id_ed25519_gl
    UserKnownHostsFile /dev/null
    StrictHostKeyChecking no
    ConnectTimeout 5
```

3. Connect VS Code to the VM [as documented here](https://code.visualstudio.com/docs/remote/ssh#_connect-to-a-remote-host)

4. In the connected VS Code window, open the directory `/run/gardenlinux-tests`

5. Ensure the `ms-python.debugpy` extension is installed



#### Cloud Environment

To connect to a cloud VM:

```bash
# Basic SSH connection
./util/login_cloud.sh .build/aws-gardener_prod-amd64-today-13371337.raw

# Execute a command directly
./util/login_cloud.sh .build/aws-gardener_prod-amd64-today-13371337.raw "uname -a"

# Run tests manually after login
cd /run/gardenlinux-tests && ./run_tests --system-booted --allow-system-modifications --expected-users gardenlinux
```

**Note**: Cloud VMs use the SSH user and IP address from the OpenTofu output.

## Test Environment Details

### Chroot Testing

- Runs tests directly in the extracted image filesystem
- Fastest execution method
- Limited to filesystem-level tests

### QEMU Testing

- Boots the image in a local QEMU virtual machine
- Full system testing including boot process
- SSH access available on localhost:2222
- Supports various architectures and boot modes (TODO)

### Cloud Testing

- Deploys the image to cloud infrastructure using OpenTofu
- Real-world environment testing
- Automatic resource cleanup (unless `--skip-cleanup` is used)
- Supports AWS, GCP, Azure, and Alibaba Cloud

## Test Distribution Build Process

The test framework is automatically built and packaged when running tests. The build process creates a self-contained distribution that includes the Python runtime, test framework, and all dependencies.

### Build Components

The build system creates several artifacts:

- **`.build/runtime.tar.gz`**: Python runtime environment with dependencies
- **`.build/dist.tar.gz`**: Test framework and test files
- **`.build/dist.ext2.raw`**: Raw ext2 filesystem image for mounting in VMs
- **`.build/dist.ext2.raw.tar.gz`**: Compressed tar file including [`disk.raw`](https://cloud.google.com/compute/docs/import/import-existing-image) Raw ext2 filesystem image to import to GCP
- **`.build/dist.vhd`**: VHD filesystem image for import in Azure
- **`.build/edk2-*`**: EDK2 firmware files for QEMU boot

### Build Process

1. **Runtime Environment**: Downloads standalone Python binaries for x86_64 and aarch64 architectures and installs required packages from `requirements.txt`
2. **Test Framework**: Bundles all test files, plugins, and the test runner script
3. **Distribution**: Creates both a compressed tar archive and an ext2 filesystem image
4. **Firmware**: Downloads EDK2 firmware files for QEMU virtualization

### Automatic Building

The build process runs automatically when you execute `./test-ng`:

```bash
# Build artifacts are created automatically
./test-ng .build/image.raw

# Or build manually
cd tests-ng
make -f util/build.makefile
```

### Test Distribution Structure

The built distribution contains:

```
dist/
├── runtime/           # Python runtime and dependencies
│   ├── x86_64/      # x86_64 Python binaries
│   ├── aarch64/     # aarch64 Python binaries
│   └── site-packages/ # Python packages
├── tests/            # Test framework and test files
│   ├── plugins/      # Test plugins
│   ├── test_*.py     # Individual test modules
│   └── conftest.py   # Pytest configuration
└── run_tests         # Test execution script
```

## Test Development

### Markers

Tests can be decorated with pytest markers to indicate certain limitations or properties of the test:

`@pytest.mark.booted(reason="Some reason, this is optional")`: This test can only be run in a booted system, not in a chroot test. Use the optional `reason` argument to document why this is needed, in cases where this is not really obvious.

`@pytest.mark.modify(reason="Some reason, this is optional")`: This test modifies the underlying system, like starting services, installing software or creating files. Use the optional `reason` argument to document why this is needed, in cases where this is not really obvious.

`@pytest.mark.root(reason="Some reason, this is optional")`: This test is run as the root user, not as an unprivileged user. Use the optional `reason` argument to document why this is needed, in cases where this is not really obvious.

`@pytest.mark.feature("a and not b", reason="Some reason, this is optional")`: This test is only run if the boolean condition is true. Use this to limit feature-specific tests. Use the optional `reason` argument to document why this is needed, in cases where this is not really obvious.

`@pytest.mark.performance_metric`: This is a performance metric test that can be skipped when running under emulation.
