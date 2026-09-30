---
title: "Setup Test Environment"
description: "Install prerequisites and dependencies for running Garden Linux tests"
related_topics:
  - /contributing/testing.md
  - /explanation/testing/test-framework-architecture.md
  - /explanation/testing/test-organization.md
  - /how-to/testing/run-tests.md
  - /how-to/testing/setup-test-environment.md
  - /how-to/testing/debug-tests.md
  - /how-to/testing/test-in-cloud.md
  - /reference/testing/developing-tests.md
  - /reference/testing/test-coverage-markers.md
  - /reference/testing/test-cli.md
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/testing/setup-test-environment.md
github_target_path: docs/how-to/testing/setup-test-environment.md
---

# Setup Test Environment

This guide explains how to install the prerequisites and dependencies needed to run Garden Linux tests.

## Prerequisites

Before running the test framework, install the following dependencies, as specified in [ADR-0016](../../reference/adr/0016-minimal-host-dependencies-for-test-ng.md):

- `podman` - Container runtime
- `make` - Build system
- `curl` - Command-line tool for transferring data
- `jq` - Command-line JSON processor
- `libxml2-utils` - XML utilities
- `unzip` - Archive extraction
- `uuid-runtime` - UUID generation utilities
- `qemu` - Machine emulator and virtualizer
- `qemu-utils` - QEMU utilities
- `socat` - Multipurpose relay tool

If you plan to provision cloud resources, the cloud provider-specific Command-Line Interfaces (CLIs) might be useful or even required:

- `azure-cli` - Azure Command-Line Interface
- `awscli` - AWS Command-Line Interface
- `gcloud` - Google Cloud Command-Line Interface
- `aliyun` - Alibaba Cloud Command-Line Interface
- `openstack-clients` - OpenStack Command-Line Interface

## Install on Debian-based systems

Install the core dependencies:

```bash
apt-get update
apt-get install podman make curl inotify-tools jq libxml2-utils unzip uuid-runtime qemu swtpm socat
```

Install cloud provider CLIs (optional):

```bash
apt-get install azure-cli awscli openstackclient
```

:::tip
For GCP and Alibaba Cloud CLIs, check the cloud provider documentation:

- [AWS CLI Installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Azure CLI Installation](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?view=azure-cli-latest&pivots=apt)
- [GCP CLI Installation](https://cloud.google.com/sdk/docs/install#deb)
- [Alibaba Cloud CLI Installation](https://www.alibabacloud.com/help/en/cli/install-cli-on-linux)
- [OpenStack CLI Installation](https://docs.openstack.org/newton/user-guide/common/cli-install-openstack-command-line-clients.html)
  :::

## Install on macOS

Install the core dependencies using Homebrew:

```bash
brew install bash coreutils curl gnu-getopt gnu-sed gnupg inotify-tools jq libxml2 make ossp-uuid podman socat swtpm unzip
```

Install cloud provider CLIs (optional):

```bash
brew install azure-cli awscli gcloud-cli aliyun-cli openstackclient
```

## Verify installation

After installation, verify that the core tools are available:

```bash
# Check podman
podman --version

# Check QEMU
qemu-system-x86_64 --version

# Check make
make --version

# Check jq
jq --version
```

## Next steps

Once the environment is set up:

1. **For cloud testing**: Configure cloud provider authentication (see [Test in Cloud](test-in-cloud.md))
2. **Run tests**: Follow the [Run Tests](run-tests.md) guide
3. **Troubleshoot issues**: See [Debug Tests](debug-tests.md) if you encounter problems

## Related topics

<RelatedTopics />
