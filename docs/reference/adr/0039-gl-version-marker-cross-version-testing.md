---
title: "ADR 0039: Version-Aware Tests for Cross-Version Test Execution"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/adr/0039-gl-version-marker-cross-version-testing.md
github_target_path: docs/reference/adr/0039-gl-version-marker-cross-version-testing.md
---

# ADR 0039: Version-Aware Tests for Cross-Version Test Execution

**Date:** 2026-09-23

## Status

Draft

## Context

The Garden Linux test framework (see
[ADR 0006](./0006-new-test-framework-in-place-self-contained-test-execution.md)
and [ADR 0010](./0010-incremental-migration-and-coexistence-of-tests.md))
ships a set of tests alongside each release. Those release-pinned tests are the
authoritative validation for that release.

We also want to prove that our newest tests hold on older releases that are
still maintained. Running the newest test suite against an older maintained
image gives us this confidence, in addition to the release-pinned tests.

Running a newer suite against an older image surfaces a problem: some tests
only make sense on newer releases (they assert behavior or configuration
introduced later), and some only make sense on older ones. Without a
declarative way to express which releases a test applies to, such runs produce
misleading failures and require ad-hoc, per-run exclusions.

Garden Linux versions follow the scheme defined in
[ADR 0011](./0011-garden-linux-versioning.md). The running version is available
on the system under test, so a test can determine at runtime whether it applies
to the current release.

## Decision

We will make tests version-aware so that a newer test suite can run against
older, still-maintained Garden Linux releases:

- Tests may declare the Garden Linux release(s) they apply to, expressed as a
  comparison against the running version.
- The framework determines the running Garden Linux version from the system
  under test and evaluates each test's declared applicability against it.
- When a test does not apply to the running version, the author can choose the
  outcome: skip the test entirely, run it but downgrade a failure to a warning,
  or run it and mark a failure as an expected failure. Downgrading failures to
  a warning is the default so that mismatches are visible without silently
  hiding tests or hard-failing the run.
- This capability is additive. Release-pinned tests continue to run unchanged;
  version-aware execution complements them.

The concrete syntax, parsing, comparison semantics, and framework wiring are
intentionally left out of this ADR and are tracked in the implementation issue.

## Consequences

### Positive

- We gain confidence that the newest tests also pass on maintained releases,
  broadening coverage beyond release-pinned tests.
- Version applicability is expressed declaratively per test, replacing ad-hoc
  per-run exclusions.
- The default "warning" outcome keeps mismatches visible without destabilizing
  runs.

### Negative

- Test authors must reason about and annotate version applicability, adding a
  small authoring burden.
- Cross-version runs can produce warnings that need triage.

### Neutral

- Developer documentation for writing tests needs to describe the new
  version-aware capability.
- Some existing tests may be annotated over time as cross-version runs reveal
  version-specific assumptions, consistent with the incremental approach in
  [ADR 0010](./0010-incremental-migration-and-coexistence-of-tests.md).
- Backporting tests to maintained releases might still be needed if the
  configuration differs too much.

## Alternatives Considered

1. **Only ever run release-pinned tests.** Rejected: this is the status quo and
   provides no signal about whether newer tests hold on maintained releases.

2. **Maintain a completely separate test suite per maintained release.** Rejected: high
   duplication and maintenance cost, and it does not prove the *newest* tests
   hold on older releases.

3. **Filter tests externally per run (CI-side allow/deny lists).** Rejected:
   applicability lives far from the test, is easy to desynchronize, and is not
   visible to test authors.
