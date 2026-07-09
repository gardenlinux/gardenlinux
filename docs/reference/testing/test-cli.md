---
title: "Test CLI Reference"
description: "Complete command-line interface reference for the Garden Linux test runner"
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
order: 3
migration_status: "done"
migration_issue: https://github.com/gardenlinux/gardenlinux/issues/4748
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/testing/test-cli.md
github_target_path: "docs/reference/testing/test-cli.md"
---

# Test CLI Reference

Complete command-line interface reference for the Garden Linux test runner (`./test`).

## Overview

The main entry point is `./test` in the Garden Linux root directory (symlink to `tests/util/run.sh`). It automatically detects the image type and runs appropriate tests.

**Basic Syntax:**

```bash
./test [OPTIONS] <image-file>
```

## Common options

### `--help`

Show help message and exit.

```bash
./test --help
```

### `--skip-cleanup`

Skip cleanup of cloud resources after testing.

**QEMU VM behavior:**

- After running or skipping tests, stop and cleanup the VM with `ctrl + c`.

**Cloud behavior:**

- To clean up cloud resources after using this flag, re-run without the flag or use `--only-cleanup`.

```bash
./test --skip-cleanup .build/image.raw
```

### `--skip-tests`

Skip running the actual test suite (useful for infrastructure setup only).

```bash
./test --skip-tests .build/image.raw
```

### `--test-args`

Pass any command-line argument to `pytest`. Put multiple arguments inside quotes.

**Examples:**

Run a specific test file:

```bash
./test --test-args "test_ssh.py" .build/image.raw
```

Run with verbose output:

```bash
./test --test-args "-v" .build/image.raw
```

Run multiple tests:

```bash
./test --test-args "test_ssh.py test_network.py -v" .build/image.raw
```

Enable debug logging:

```bash
./test --test-args "--log-cli-level=DEBUG" .build/image.raw
```

## Cloud-specific options

### `--cloud <provider>`

Specify cloud provider (aws, gcp, azure, ali, openstack).

```bash
./test --cloud aws .build/image.raw
./test --cloud gcp .build/image.raw
./test --cloud azure .build/image.raw
./test --cloud ali .build/image.raw
./test --cloud openstack .build/image.raw
```

:::info
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

### `--image-requirements-file <file>`

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

:::info
QEMU VM testing ignores this flag.
:::

## QEMU-specific options

### `--ssh`

Enable SSH access to QEMU VM (`gardenlinux@127.0.0.1:2222`).

```bash
./test --ssh .build/image.raw
```

:::info
For cloud testing, SSHD is always enabled via `cloud-init`.
:::

### `--debug`

Enable debug mode (display window) for QEMU VM.

```bash
./test --debug .build/image.raw
```

Shows a graphical window with the QEMU VM console output.

## Development options

### `--dev`

Enable development mode with automatic file synchronization and test re-execution.

**QEMU shorthand for:**

```bash
--ssh --skip-cleanup --skip-tests --watch
```

**Cloud shorthand for:**

```bash
--skip-cleanup --skip-tests --watch
```

**Usage:**

```bash
# QEMU dev mode
./test --dev .build/image.raw

# Cloud dev mode
./test --dev --cloud aws .build/image.raw

# With specific tests
./test --dev --test-args "test_ssh.py -v" .build/image.raw
```

**What it does:**

1. Starts VM (QEMU or cloud)
2. Syncs test distribution
3. Runs tests once
4. Watches for file changes in `tests/` and `features/`
5. Re-syncs and re-runs tests on changes
6. Stop with `Ctrl+C`

### `--watch`

Watch for file changes and re-run tests automatically (used internally by `--dev`).

```bash
./test --ssh --skip-cleanup --skip-tests --watch .build/image.raw
```

## Image types

The test runner automatically detects the image type based on the file extension:

**`.tar` files** - Chroot testing:

```bash
./test .build/image.tar
```

**`.raw` files** - QEMU or cloud testing:

```bash
# QEMU (default)
./test .build/image.raw

# Cloud (with --cloud flag)
./test --cloud aws .build/image.raw
```

**`.oci` files** - OCI container testing:

```bash
./test .build/container-amd64-today-local.oci
```

## Examples

### Basic testing

Run chroot tests:

```bash
./test .build/image.tar
```

Run QEMU tests:

```bash
./test .build/image.raw
```

Run cloud tests:

```bash
./test --cloud aws .build/image.raw
```

### Development workflow

Run QEMU with SSH and keep running:

```bash
./test --ssh --skip-cleanup .build/image.raw
```

Use dev mode for rapid iteration:

```bash
./test --dev --test-args "test_ssh.py -v" .build/image.raw
```

### Specific test execution

Run only SSH tests:

```bash
./test --test-args "test_ssh.py" .build/image.raw
```

Run tests with verbose output:

```bash
./test --test-args "-v" .build/image.raw
```

Run multiple specific tests:

```bash
./test --test-args "test_ssh.py test_network.py -v" .build/image.raw
```

### Cloud testing

Test on AWS with cleanup:

```bash
./test --cloud aws .build/image.raw
```

Test on AWS, keep resources for inspection:

```bash
./test --cloud aws --skip-cleanup .build/image.raw
```

Clean up resources later:

```bash
./test --cloud aws --only-cleanup .build/image.raw
```

Test existing cloud image:

```bash
./test --cloud aws --skip-cleanup --skip-tests --cloud-image \
  --image-requirements-file .build/aws-gardener_prod-amd64-today-local.requirements \
  ami-07f977508ed36098e
```

### Debugging

Enable debug logging:

```bash
./test --test-args "--log-cli-level=DEBUG" .build/image.raw
```

Run specific test with debug logging:

```bash
./test --test-args "--log-cli-level=DEBUG test_ssh.py" .build/image.raw
```

Show QEMU debug window:

```bash
./test --debug .build/image.raw
```

### Infrastructure only

Set up infrastructure without running tests:

```bash
./test --skip-tests .build/image.raw
```

Plan cloud resources without creating them:

```bash
./test --cloud aws --cloud-plan .build/image.raw
```

## Option combinations

Common option combinations:

**Local development:**

```bash
./test --ssh --skip-cleanup .build/image.raw
```

**Rapid iteration:**

```bash
./test --dev --test-args "test_ssh.py -v" .build/image.raw
```

**Cloud inspection:**

```bash
./test --cloud aws --skip-tests --skip-cleanup .build/image.raw
```

**Specific test in cloud:**

```bash
./test --cloud aws --skip-cleanup --test-args "test_ssh.py -v" .build/image.raw
```

**Debug mode with SSH:**

```bash
./test --ssh --debug --skip-cleanup .build/image.raw
```

## Exit codes

The test runner returns standard pytest exit codes:

- `0` - All tests passed
- `1` - Tests failed
- `2` - Test execution was interrupted
- `3` - Internal error during test execution
- `4` - pytest command-line usage error
- `5` - No tests were collected

## Related Topics

<RelatedTopics />
