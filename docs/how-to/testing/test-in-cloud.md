---
title: "Test in Cloud"
description: "Run Garden Linux tests on cloud providers with authentication and configuration guides"
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
github_source_path: docs/how-to/testing/test-in-cloud.md
github_target_path: "docs/how-to/testing/test-in-cloud.md"
---

# Test in Cloud

This guide explains how to run Garden Linux tests on cloud providers including authentication setup and cloud-specific options.

## Overview

Cloud testing deploys the image to cloud infrastructure using OpenTofu, providing real-world environment testing with automatic resource cleanup.

**Supported Providers:**

- Amazon Web Services (AWS)
- Microsoft Azure
- Google Cloud Platform (GCP)
- Alibaba Cloud (ALI)
- OpenStack

## Cloud Provider Authentication

Before running tests, authenticate with the cloud providers you want to test against. Each provider has its own authentication method.

### Alibaba Cloud (ALI)

Alibaba Cloud requires you to set up an [AccessKey pair](https://www.alibabacloud.com/help/en/cli/configure-credentials#0da5d08f581wn):

```bash
# Select profile
export ALIBABA_CLOUD_PROFILE=gardenlinux-test

# Configure your existing ALI credentials (only needed once)
aliyun configure --profile $ALIBABA_CLOUD_PROFILE

# Check access
aliyun sts GetCallerIdentity
```

### Amazon Web Services (AWS)

AWS requires [IAM user credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-authentication-user.html):

```bash
# Select profile
export AWS_PROFILE=gardenlinux-test

# Configure your existing AWS credentials (only needed once)
aws configure

# Check access
aws sts get-caller-identity
```

:::note
For AWS, you can also use Single Sign-On (SSO) authentication if your organization supports it.
:::

### Microsoft Azure

Azure requires [user authentication via Azure CLI](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli):

```bash
# Configure your existing Azure Subscription
export ARM_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Login
az login

# Check access
az account show
```

:::note
The subscription ID can be found in the Azure portal under Subscriptions.
:::

### Google Cloud Platform (GCP)

GCP requires [user authentication via gcloud CLI](https://cloud.google.com/docs/authentication/gcloud):

```bash
# Configure your existing Google Cloud Project
export GOOGLE_PROJECT="gardenlinux-test"

# Configure your existing GCP credentials (only needed once)
gcloud config set project ${GOOGLE_PROJECT}

# Login
gcloud auth application-default login

# Check access
gcloud auth list
```

:::note
The Project ID can be found in the Google Cloud portal under Project info.
:::

### OpenStack

Configure OpenStack authentication:

```bash
# Download or configure ~/.config/openstack/clouds.yaml
# Select profile
export OS_CLOUD=gardenlinux-test
```

:::note
You can download the `clouds.yaml` from your OpenStack dashboard.
:::

## Cloud-Specific Command-Line Options

### `--cloud <provider>`

Specify the cloud provider (aws, gcp, azure, ali, openstack).

```bash
./test --cloud aws .build/image.raw
```

:::note
QEMU VM testing ignores this flag.
:::

### `--cloud-image`

Use an existing cloud image instead of uploading a new one.

Possible images are listed on official releases, for example [1592.12](https://github.com/gardenlinux/gardenlinux/releases/tag/1592.12):

- ali: `m-d7o7skltl4qe9anmwdp4` (eu-west-1 amd64)
- aws: `ami-0d8d06eb3a44ae794` (eu-central-1 amd64)
- gcp: `gardenlinux-gcp-ff804026cbe7b5f2d6f729e4-1592-12-c6d7f9a9` (amd64)
- azure: `/CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-gen2/Versions/1592.12.0` (amd64)

```bash
./test --cloud aws --cloud-image ami-0d8d06eb3a44ae794
```

### `--image-requirements-file`

Only needed with `--cloud-image`. Points to a valid `*.requirements` file.

```bash
./test --cloud aws --cloud-image \
  --image-requirements-file .build/aws-gardener_prod-amd64-today-local.requirements \
  ami-07f977508ed36098e
```

### `--only-cleanup`

Only run `tofu destroy` for cloud setups (cleans up resources without running tests).

```bash
./test --cloud aws --only-cleanup .build/image.raw
```

### `--cloud-plan`

Only run `tofu plan` for cloud setups (shows what resources would be created without creating them).

```bash
./test --cloud aws --cloud-plan .build/image.raw
```

:::note
QEMU VM testing ignores this flag.
:::

## Examples

### Basic Cloud Testing

Test on AWS:

```bash
./test --cloud aws .build/image.raw
```

Test on Azure:

```bash
./test --cloud azure .build/image.raw
```

Test on GCP:

```bash
./test --cloud gcp .build/image.raw
```

### Testing with Resource Inspection

Keep resources running after tests for inspection:

```bash
./test --cloud aws --skip-cleanup .build/image.raw
```

Clean up resources later:

```bash
./test --cloud aws --only-cleanup .build/image.raw
```

### Testing Existing Cloud Images

Test an existing AWS AMI:

```bash
./test --cloud aws --skip-cleanup --skip-tests --cloud-image \
  --image-requirements-file .build/aws-gardener_prod-amd64-today-local.requirements \
  ami-07f977508ed36098e
```

### Infrastructure Setup Only

Set up infrastructure without running tests:

```bash
./test --cloud aws --skip-tests --skip-cleanup .build/image.raw
```

### Planning Infrastructure Changes

See what resources would be created:

```bash
./test --cloud aws --cloud-plan .build/image.raw
```

### Running Specific Tests

Run only specific tests on cloud:

```bash
./test --cloud aws --skip-cleanup \
  --test-args "test_ssh.py test_aws.py -v" \
  .build/image.raw
```

## Resource Management

### Automatic Cleanup

By default, cloud resources are automatically cleaned up after tests complete:

```bash
./test --cloud aws .build/image.raw
# Resources are automatically destroyed
```

### Manual Cleanup

Skip automatic cleanup for investigation:

```bash
# Run tests and keep resources
./test --cloud aws --skip-cleanup .build/image.raw

# Manually clean up later
./test --cloud aws --only-cleanup .build/image.raw
```

### Cleanup After Interruption

If tests are interrupted with `--skip-cleanup`, re-run without the flag or use `--only-cleanup`:

```bash
# Tests were interrupted with --skip-cleanup
# Clean up by re-running without the flag
./test --cloud aws .build/image.raw

# Or use --only-cleanup
./test --cloud aws --only-cleanup .build/image.raw
```

## Troubleshooting

### Authentication Issues

If authentication fails, verify:

1. Environment variables are set correctly
2. Credentials are valid and not expired
3. Required permissions are granted
4. CLI tools are installed and configured

### Resource Cleanup Failures

If cleanup fails:

1. Use `--only-cleanup` to retry cleanup
2. Check cloud provider console for orphaned resources
3. Manually delete resources if automatic cleanup fails

### Timeout Issues

Cloud resource provisioning can take time. If tests timeout:

1. Check cloud provider status pages for outages
2. Verify network connectivity
3. Try a different region

## Related Topics

<RelatedTopics />
