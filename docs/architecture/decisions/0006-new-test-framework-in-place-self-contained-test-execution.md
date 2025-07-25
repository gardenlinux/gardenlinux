# 6. New Test Framework to enable In-Place, Self-Contained Test Execution

**Date:** 2025-07-25

## Status

Accepted

## Context

The current Garden Linux test framework executes tests remotely via SSH from a developer’s machine or CI runner. This approach requires enabling SSH on the system under test, may install packages or mutate system state, and is unsuitable for production or long-lived systems. The framework’s distribution and execution model is tightly coupled to ephemeral build artifacts and remote access, limiting portability and safety.

Key limitations:
- **System Mutation:** SSH setup and package installation modify the system under test.
- **Remote Execution Model:** Tests require remote connectivity and SSH, which is not always available or desirable.
- **Limited Portability:** The framework cannot be easily run in containers, chroots, or production environments.
- **Operational Risk:** Running tests on production systems risks unintended changes.

## Decision

We will redesign the test framework to execute tests directly on the target system (“in-place”), using a self-contained test suite distribution. The test suite will be packaged as a relocatable directory or tarball, including:
- A standalone Python runtime
- All dependencies (including pytest)
- All test code

The only requirement on the target system will be a working `libc`. Tests will be executed locally, without requiring SSH or remote connectivity. Deployment mechanisms may include `scp`, `docker cp`, bind mounts, volume attach, or other means suitable for the environment.

Running tests on a developer machine will not require multiple invocations of `make`, building and testing an image are a single script invocation each.

## Consequences

- **Safety:** The system under test is not mutated by the test framework (no SSH setup, no package installs, no filesystem changes).
- **Portability:** The test suite can run in containers, chroots, VMs, bare metal, and production systems.
- **Flexibility:** Multiple deployment mechanisms are supported; the framework is not tied to a specific transport or runtime.
- **Maintainability:** The framework is easier to reason about and maintain, as tests run in a predictable, local context.
- **Reporting:** Output can be collected via stdout/stderr, persisted as JUnit XML, or exported in other formats.
- **Migration:** Enables incremental migration; old and new frameworks can coexist during transition.

## Alternatives Considered

We evaluated packaging the test suite as an [OCI container](https://opencontainers.org) and leveraging [systemd system extensions](https://www.freedesktop.org/software/systemd/man/latest/systemd-sysext.html) for deployment.

These approaches were not adopted due to the following limitations:
- **Software Availability:** Container runtimes and systemd are not present in all target environments.
- **Permission Requirements:** Both methods require elevated privileges, which may not be feasible or desirable in production or restricted systems.
