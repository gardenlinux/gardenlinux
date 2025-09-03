# ADR 0007: Non-Invasive, Read-Only Testing

**Date:** 2025-07-25

## Status

Accepted

## Context

See [6. New Test Framework to enable In-Place, Self-Contained Test Execution](./0006-new-test-framework-in-place-self-contained-test-execution.md) for additional context on this decision.

The current Garden Linux test framework modifies the system under test by enabling SSH, installing packages, and making other system-level changes. This approach is suitable for disposable, ephemeral systems but is unsafe for production or long-lived environments, where any mutation can introduce risk, instability, or compliance issues.

Key limitations:
- **System Mutation:** Tests may alter system configuration, install software, or change files, making the framework unsuitable for production validation.
- **Operational Risk:** Running tests on production systems risks unintended changes, outages, or security issues.
- **Limited Applicability:** The framework cannot be safely used on systems that must remain unchanged, such as production servers or persistent VMs.

## Decision
The redesigned test framework will treat the system under test as read-only by default. Tests must not modify system state, install packages, enable services, or change configuration unless explicitly permitted. Tests that require modification of global system state (such as loading kernel modules) **MUST** be clearly marked using a dedicated pytest marker. These tests will be skipped unless the test framework is run with an explicit argument to allow modifications. As a result, mutating tests will only be executed on ephemeral targets, such as local test VMs or during platform tests, ensuring production and persistent systems remain unaffected.

## Consequences

- **Safety:** Tests can be run on production, long-lived, or critical systems without risk of mutation or disruption.
- **Compliance:** The framework supports environments with strict change control or audit requirements.
- **Broader Applicability:** Enables validation of systems in a wider range of scenarios, including live production, cloud, and edge environments.
- **Test Design:** All tests must either avoid mutating the system, or declare that they need to mutate the system state.
- **Migration:** Existing tests must be audited and refactored to ensure compliance with the requirement.

