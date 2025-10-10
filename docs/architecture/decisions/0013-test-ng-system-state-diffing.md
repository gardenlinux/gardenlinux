# ADR 0013: System State Diffing in tests-ng

**Date:** 2025-10-07

## Status

Accepted

## Context

See related ADRs for the evolution of the next-generation test framework:

- [0006: New Test Framework to enable In-Place, Self-Contained Test Execution](./0006-new-test-framework-in-place-self-contained-test-execution.md)
- [0007: Non-Invasive, Read-Only Testing](./0007-non-invasive-read-only-testing.md)
- [0008: Unified and Declarative Test Logic](./0008-unified-and-declarative-test-logic.md)
- [0009: Flexible Distribution and Reporting](./0009-flexible-distribution-and-reporting.md)
- [0010: Incremental Migration and Coexistence of Tests](./0010-incremental-migration-and-coexistence-of-tests.md)

The tests-ng framework emphasizes non-invasive testing while acknowledging that some tests may modify the system (e.g., enabling services, installing packages, adjusting kernel parameters). Today, unintended modifications can slip through and only surface later, complicating root cause analysis.

We need a reliable, extensible way to detect and report any system state changes introduced during a test run, so we can:

- Ensure tests that are intended to be read-only actually are.
- Attribute modifications to specific tests and make them explicit.

## Decision

Introduce a tests-ng plugin ("sysdiff") that captures a snapshot of system state before tests start and compares it with a snapshot after tests finish. The plugin runs in a well-defined order (using the pytest ordering plugin) to bracket the entire test session.

Scope of collected state (initial set, extensible):

- Installed packages (dpkg).
- Systemd unit states.
- Filesystem checksums for selected paths.
- Sysctl parameters.
- Loaded kernel modules.

Implementation choices:

- Snapshots are stored in the invoking user's data directory at `~/.local/state/sysdiff/`. This allows (in theory) that it can be run by any user.
- Each state domain may define static ignore/allow lists for noisy or frequently changing items (e.g., `IGNORED_SYSCTL_PARAMS`, `IGNORED_SYSTEMD_PATTERNS`, `IGNORED_KERNEL_MODULES`). These lists are implemented as constants in the sysdiff plugin itself.
- The comparison produces a human-readable unified diff per domain. If changes are detected, the end-of-run check fails the test session with a consolidated report.
- Development of `sysdiff` can easily be tested with python script in `tests-ng/util/sysdiff.py`.

Developer experience:

- Tests that intentionally modify the system should be annotated accordingly (e.g., using established markers).
- The plugin is designed to be easily extended with additional collectors and refined ignore rules as more and more tests are ported and potential state domains are discovered.

## Consequences

Positive:

- Increased confidence that tests are non-invasive by default, surfacing unexpected changes immediately.
- Makre sure that invasive tests do not permanently change the system state.
- Faster triage: diffs point to the exact domain (packages, systemd, sysctl, modules, files), reducing time-to-root-cause.

Trade-offs and risks:

- Additional runtime overhead to compute snapshots and diffs; should be mitigated by keeping sysdiff's footprint small.
- Requires maintenance of ignore/allow lists to avoid flaky diffs on expected dynamics; this is an ongoing curation task.
- Initial failures in CI are expected while the baseline ignore lists are tuned and tests are made explicit about intended modifications.

## Alternatives Considered

- Rely solely on conventions, documentation and developer experience to keep tests non-invasive: insufficient enforcement; regressions would continue to slip through.
- Post-hoc log analysis to infer modifications: indirect, incomplete, and harder to make actionable.
- The [Landlock LSM](https://www.man7.org/linux/man-pages/man7/Landlock.7.html) could further improve the test framwork to run in a sandbox. This however does not solve the issue of comparing the system state before and after the test runs.

## References

- [Initial feature proposal and discussion](https://github.com/gardenlinux/gardenlinux/issues/3488)
- [Pull request introducing the sysdiff plugin](https://github.com/gardenlinux/gardenlinux/pull/3506)
