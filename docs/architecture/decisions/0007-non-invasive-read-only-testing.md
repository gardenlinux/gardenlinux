# ADR 0007: Non-Invasive, Read-Only Testing

**Date:** 2025-07-25

## Status

Accepted

## Context

The current Garden Linux test framework modifies the system under test by enabling SSH, installing packages, and making other system-level changes. This approach is suitable for disposable, ephemeral systems but is unsafe for production or long-lived environments, where any mutation can introduce risk, instability, or compliance issues.

Key limitations:
- **System Mutation:** Tests may alter system configuration, install software, or change files, making the framework unsuitable for production validation.
- **Operational Risk:** Running tests on production systems risks unintended changes, outages, or security issues.
- **Limited Applicability:** The framework cannot be safely used on systems that must remain unchanged, such as production servers or persistent VMs.

## Decision

The redesigned test framework will treat the system under test as strictly read-only. Tests must not modify system state, install packages, enable services, or change configuration. The framework itself will not require SSH setup or any other mutation of the target system. All test logic must operate without side effects, ensuring that the system remains unchanged before, during, and after test execution.

## Consequences

- **Safety:** Tests can be run on production, long-lived, or critical systems without risk of mutation or disruption.
- **Compliance:** The framework supports environments with strict change control or audit requirements.
- **Broader Applicability:** Enables validation of systems in a wider range of scenarios, including live production, cloud, and edge environments.
- **Test Design:** All tests must be written to avoid side effects; destructive or mutating tests are prohibited.
- **Migration:** Existing tests must be audited and refactored to ensure compliance with the read-only requirement.

