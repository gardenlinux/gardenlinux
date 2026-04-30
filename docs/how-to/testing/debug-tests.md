---
title: "Debug Tests"
description: Learn how to Troubleshoot and Debug Garden Linux Tests
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
migration_source: "tests/README.md, tests/DEVELOPER.md"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/testing/debug-tests.md
github_target_path: "docs/how-to/testing/debug-tests.md"
---

# Debug Tests

This guide explains how to troubleshoot and debug Garden Linux tests when they fail or behave unexpectedly.

## Debugging Approaches

The test framework provides several debugging approaches:

- **Debug logs** - Understand what the test framework and plugins are doing internally
- **Login scripts** - Interactively investigate the test environment (QEMU VMs or cloud instances)
- **Dev mode** - Rapidly iterate on tests with automatic synchronization
- **Manual test execution** - Run tests directly inside the test environment

Choose the approach based on your needs: inspect framework behavior, investigate system state, or manually verify test conditions.

## Debug Logs

Enable debug-level logging to see detailed information about plugin operations, system interactions, and test execution flow.

### Enable Debug Logging

Enable debug logging for all components:

```bash
./test --test-args "--log-cli-level=DEBUG" .build/image.raw
```

Enable debug logging for a specific test:

```bash
./test --test-args "--log-cli-level=DEBUG test_ssh.py" .build/image.raw
```

:::important
Tests need to implement debug output. Results may vary depending on the test.
:::

### Debug Output in Tests

For information on adding debug output to tests, see [Developing Tests](../reference/testing/developing-tests.md#debugging-tests).

## Login Scripts

Use login scripts to access running VMs for interactive investigation. Once connected, you can explore the filesystem, check service status, examine logs, and run tests manually.

### QEMU Environment

Connect to a running QEMU VM:

```bash
# Get an SSH session
./util/login_qemu.sh

# Get an SSH session with custom user
./util/login_qemu.sh --user admin

# Execute a command directly
./util/login_qemu.sh "uname -a"

# Run tests manually after login
cd /run/gardenlinux-tests && ./run_tests --system-booted --allow-system-modifications --expected-users gardenlinux

# Run tests with sudo if you need root privileges
cd /run/gardenlinux-tests && sudo ./run_tests --system-booted --allow-system-modifications --expected-users gardenlinux
```

:::important
Login to QEMU VMs is only possible if `--ssh --skip-cleanup` is passed when starting the test. Secure Shell Daemon (SSHD) is reachable on `127.0.0.1:2222` with the user `gardenlinux`. The QEMU VM stays open in the shell that started the test and can be stopped with `ctrl + c`.
:::

**Common debugging workflow:**

1. Start tests with `--ssh --skip-cleanup` to keep the VM running
2. In a separate terminal, use `./util/login_qemu.sh` to connect
3. Investigate the system state, check logs, or run tests manually
4. Return to the original terminal and stop the VM with `ctrl + c` when done

### Cloud Environment

Connect to a cloud VM:

```bash
# Basic SSH connection
./util/login_cloud.sh .build/aws-gardener_prod-amd64-today-13371337.raw

# Execute a command directly
./util/login_cloud.sh .build/aws-gardener_prod-amd64-today-13371337.raw "uname -a"

# Run tests manually after login
cd /run/gardenlinux-tests && ./run_tests --system-booted --allow-system-modifications --expected-users gardenlinux

# Run tests with sudo if you need root privileges
cd /run/gardenlinux-tests && sudo ./run_tests --system-booted --allow-system-modifications --expected-users gardenlinux
```

:::important
Cloud VMs use the SSH user and Internet Protocol (IP) address from the OpenTofu output. The login script automatically retrieves this information from the Terraform state.
:::

**Common debugging workflow:**

1. Start tests with `--skip-cleanup` to keep the cloud instance running
2. Use `./util/login_cloud.sh` with the image file to connect
3. Investigate the system state, check logs, or run tests manually
4. Re-run tests without `--skip-cleanup` or use `--only-cleanup` to clean up resources when done

## Dev Mode (Rapid Iteration)

Use the `--dev` flag to quickly iterate on tests with automatic file synchronization and re-execution.

### QEMU Dev Mode

Start a QEMU VM in dev mode:

```bash
./test --dev .build/aws-gardener_prod-amd64-today-local.raw
```

With specific tests:

```bash
./test --dev --test-args "test_ssh.py -v" .build/aws-gardener_prod-amd64-today-local.raw
```

**What happens:**

1. Starts a QEMU VM
2. Syncs `.build/dist.tar.gz` into the VM
3. Syncs the current `tests/` tree
4. Runs `pytest` inside the VM with the provided `--test-args`
5. Waits for file changes in `tests/` and `features/`
6. Re-syncs changed tests into the VM
7. Re-runs `pytest` with your given arguments after each change

Stop watch mode at any time with `Ctrl+C`.

:::note
`--dev` is shorthand for `--ssh --skip-cleanup --skip-tests --watch`.
:::

### Cloud Dev Mode

Start a cloud VM in dev mode:

```bash
./test --dev --cloud azure .build/azure-gardener_prod-amd64-today-local.raw
```

Or use an already uploaded image:

```bash
./test --dev --cloud azure \
  --cloud-image --image-requirements-file .build/azure-gardener_prod-amd64-today-local.requirements \
  /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-gardener_prod-amd64/Versions/2150.0.0
```

With specific tests:

```bash
./test --dev --cloud azure --test-args "test_ssh.py -v" .build/image.raw
```

**What happens:**

1. Deploys a cloud VM
2. Syncs `.build/dist.tar.gz` into the VM
3. Syncs the current `tests/` tree
4. Runs `pytest` inside the VM with the provided `--test-args`
5. Waits for file changes in `tests/` and `features/`
6. Re-syncs changed tests into the VM
7. Re-runs `pytest` with your given arguments after each change

Stop watch mode at any time with `Ctrl+C`.

:::note
`--dev` is shorthand for `--skip-cleanup --skip-tests --watch` in cloud mode.
:::

### Chroot Dev Mode

The `--dev` flag works the same way in chroot environments:

```bash
./test --dev .build/image.tar
```

## Common Debugging Scenarios

### Test Fails Unexpectedly

1. Enable debug logging to see what is happening:

   ```bash
   ./test --test-args "--log-cli-level=DEBUG test_failing.py" .build/image.raw
   ```

2. Run the test in isolation to rule out dependencies:

   ```bash
   ./test --test-args "test_failing.py::test_specific_function -v" .build/image.raw
   ```

3. Use dev mode to iterate quickly:
   ```bash
   ./test --dev --test-args "test_failing.py -v" .build/image.raw
   ```

### Test Passes Locally But Fails in Continuous Integration (CI)

1. Test in the same environment as CI (cloud testing):

   ```bash
   ./test --cloud aws .build/image.raw
   ```

2. Check for environment-specific issues (markers, dependencies)

3. Enable debug logging in CI by modifying test arguments

### Need to Inspect System State

1. Start VM with cleanup disabled:

   ```bash
   ./test --ssh --skip-cleanup .build/image.raw
   ```

2. Login to inspect:

   ```bash
   ./util/login_qemu.sh
   ```

3. Check logs, services, files:
   ```bash
   journalctl -xe
   systemctl status
   ls -la /etc/
   ```

### Test Takes Too Long to Run

1. Run only the specific test:

   ```bash
   ./test --test-args "test_specific.py" .build/image.raw
   ```

2. Use chroot for faster iteration (if applicable):

   ```bash
   ./test .build/image.tar
   ```

3. Skip expensive tests during development:
   ```bash
   ./test --test-args "-m 'not slow'" .build/image.raw
   ```

## Troubleshooting Tips

### Connection Issues

If you cannot connect to a VM:

- Verify `--ssh` flag is used for QEMU
- Check that `--skip-cleanup` is used
- Verify VM is still running
- Check firewall rules for cloud VMs

### File Synchronization Issues in Dev Mode

If changes are not synced in dev mode:

- Ensure files are saved
- Check file paths match expected locations
- Verify `inotify-tools` is installed
- Look for errors in the watch mode output

### Permission Issues

If tests fail with permission errors:

- Check if tests require root privileges (should use `@pytest.mark.root`)
- Use `sudo` when running tests manually if needed
- Verify file permissions in the test environment

### Test Environment Differences

If tests behave differently across environments:

- Check test markers (`@pytest.mark.booted`, `@pytest.mark.feature`)
- Verify the test is appropriate for the environment
- Check for environment-specific configurations

## Related Topics

<RelatedTopics />
