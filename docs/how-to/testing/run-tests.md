---
title: "Run Tests"
description: "How to run Garden Linux tests in chroot, QEMU, cloud, OCI, and Kubernetes environments"
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
migration_status: "done"
migration_issue: https://github.com/gardenlinux/gardenlinux/issues/4748
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/testing/run-tests.md
github_target_path: docs/how-to/testing/run-tests.md
---

# Run Tests

This guide explains how to run Garden Linux tests in various environments including chroot, QEMU, cloud providers, OCI containers, and Kubernetes clusters.

## Quick Start

The main entry point is `./test` in the Garden Linux root directory (symlink to `tests/util/run.sh`). It automatically detects the image type and runs appropriate tests:

```bash
# For chroot testing (tar files)
./test .build/$image.tar

# For QEMU VM testing (raw files)
./test .build/$image.raw

# For cloud provider testing (raw files only)
./test --cloud aws .build/$image.raw
./test --cloud gcp .build/$image.raw
./test --cloud azure .build/$image.raw
./test --cloud ali .build/$image.raw
```

:::tip
Use `./test --help` to see all available options and examples.
:::

## Test Environments

Garden Linux supports testing in multiple environments, each with different characteristics:

### Chroot Testing

Runs tests directly in the extracted image filesystem.

**Characteristics:**

- Fastest execution method
- Limited to filesystem-level tests
- No boot process involved
- No network or services running

**Usage:**

```bash
./test .build/image.tar
```

### QEMU Testing

Boots the image in a local QEMU virtual machine.

**Characteristics:**

- Full system testing including boot process
- SSH access available on localhost:2222
- Supports various architectures and boot modes
- Suitable for local development and testing

**Usage:**

```bash
# Basic QEMU testing
./test .build/image.raw

# With SSH access
./test --ssh .build/image.raw

# With debug window
./test --debug .build/image.raw

# Keep VM running after tests
./test --ssh --skip-cleanup .build/image.raw
```

### Cloud Testing

Deploys the image to cloud infrastructure using OpenTofu.

**Characteristics:**

- Real-world environment testing
- Automatic resource cleanup (unless `--skip-cleanup` is used)
- Supports AWS, GCP, Azure, Alibaba Cloud, and OpenStack
- Tests cloud-specific integrations

**Usage:**

```bash
# Test on AWS
./test --cloud aws .build/image.raw

# Test on Azure
./test --cloud azure .build/image.raw

# Test on GCP
./test --cloud gcp .build/image.raw

# Test on Alibaba Cloud
./test --cloud ali .build/image.raw

# Skip cleanup to inspect resources
./test --cloud aws --skip-cleanup .build/image.raw
```

See [Test in Cloud](test-in-cloud.md) for detailed cloud provider setup and authentication.

### OCI Testing

Runs tests in containers based on a Base Image.

**Characteristics:**

- Very fast execution method
- Limited to Base Image (Bare Flavors are not currently supported)
- Limited to unbooted system
- Suitable for quick validation

**Usage:**

```bash
./test .build/container-amd64-today-local.oci
```

### Kubernetes Cluster Testing

The test framework can run directly on a live Gardener cluster (or any Kubernetes cluster running Garden Linux nodes).

Deploy the following YAML:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test
spec:
  hostPID: true
  restartPolicy: Never
  containers:
    - name: test
      image: ghcr.io/gardenlinux/test:nightly
      securityContext:
        privileged: true
      args: ["./run_tests", "--system-booted", "--expected-users", "gardener"]
```

After deployment, retrieve test results from pod logs:

```bash
kubectl logs test
```

To get JUnit Extensible Markup Language (XML) output, adjust the `args` and mount a volume:

```yaml
args:
  [
    "./run_tests",
    "--junit-xml",
    "output/test.xml",
    "--system-booted",
    "--expected-users",
    "gardener",
  ]
```

:::note
The `ghcr.io/gardenlinux/test:nightly` container is built and published daily to provide the most up-to-date variant of the test framework. Per-release variants will be available in future releases.
:::

## Common Command-Line Options

### General Options

**`--help`**
: Show help message and exit.

**`--skip-cleanup`**
: Skip cleanup of cloud resources after testing.

- QEMU VM: Stop and cleanup the VM with `ctrl + c` after running or skipping tests.
- Cloud: Re-run without the flag or use `--only-cleanup` to clean up cloud resources.

**`--skip-tests`**
: Skip running the actual test suite (useful for infrastructure setup only).

**`--test-args`**
: Pass any command-line argument to `pytest`. Put multiple arguments inside `""`.

Example:

```bash
./test --test-args "test_ssh.py -v" .build/image.raw
```

## Examples

Run chroot tests on a tar image:

```bash
./test .build/aws-gardener_prod-amd64-today-13371337.tar
```

Run OCI container tests on Base Image:

```bash
./test .build/container-amd64-today-local.oci
```

Run QEMU tests with SSH access and skip cleanup:

```bash
./test --ssh --skip-cleanup .build/aws-gardener_prod-amd64-today-13371337.raw
```

Run cloud tests on AWS, skipping cleanup:

```bash
./test --cloud aws --skip-cleanup .build/aws-gardener_prod-amd64-today-13371337.raw
```

Run cloud tests but skip the test execution and cleanup:

```bash
./test --cloud aws --skip-tests --skip-cleanup .build/aws-gardener_prod-amd64-today-13371337.raw
```

Run QEMU tests and only run test_ssh.py in verbose mode:

```bash
./test --test-args "test_ssh.py -v" .build/aws-gardener_prod-amd64-today-13371337.raw
```

Run cloud tests, skip cleanup, and only run test_ssh.py and test_aws.py in verbose mode:

```bash
./test --cloud aws --skip-cleanup --test-args "test_ssh.py test_aws.py -v" .build/aws-gardener_prod-amd64-today-13371337.raw
```

Spin up an existing cloud image using image requirements file:

```bash
./test --cloud aws --skip-cleanup --skip-tests --cloud-image \
  --image-requirements-file .build/aws-gardener_prod-amd64-today-local.requirements \
  ami-07f977508ed36098e
```

## Related Topics

<RelatedTopics />
