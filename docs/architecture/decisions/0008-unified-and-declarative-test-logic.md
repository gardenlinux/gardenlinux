# ADR 0008: Unified and Declarative Test Logic

**Date:** 2025-07-25

## Status

Accepted

## Context

The current Garden Linux test framework uses fragmented and inconsistent mechanisms for conditional test execution and privilege handling. Tests are skipped or included based on a combination of feature directories, `.disable` files, and ad-hoc fixtures with inconsistent naming conventions. Privilege escalation is handled manually via `sudo` calls in test code, which is error-prone and difficult to maintain. Test logic is often split between thin wrappers and global helper functions, making it hard to understand what a test actually verifies.

Key limitations:
- **Fragmented Skipping Logic:** Multiple, overlapping mechanisms for feature and platform-based skipping make test inclusion opaque and hard to reason about.
- **Manual Privilege Handling:** Tests requiring root privileges must invoke `sudo` manually, with no automatic skipping or privilege management.
- **Opaque Test Logic:** Test assertions are often hidden in helper functions, reducing readability and maintainability.

## Decision

We will adopt a unified, declarative approach for test logic, conditional skipping, and privilege handling:

- **Feature and Platform Skipping:** All conditional test execution will use explicit, declarative markers (e.g., `@pytest.mark.feature("expression")`, `@pytest.mark.booted`). Boolean logic in markers will allow precise control over test inclusion.
- **Privilege Handling:** Tests requiring root privileges will be marked with `@pytest.mark.root`. The framework will automatically skip these tests when running unprivileged, or drop privileges for tests that do not require root.
- **Direct Test Assertions:** Tests will include assertions and logic directly, using fixtures for abstraction where needed. Helper functions will be used only for reusable logic, not for hiding test assertions.

## Consequences

- **Clarity:** Test inclusion and skipping are easy to understand by inspecting the test file; no more hidden or implicit logic.
- **Maintainability:** Consistent use of markers and fixtures makes the test suite easier to maintain and extend.
- **Safety:** Automatic privilege management reduces risk of accidental system mutation or privilege escalation.
- **Expressiveness:** Boolean logic in markers allows complex conditional test execution without convoluted fixtures or directory structures.
- **Migration:** Existing tests must be refactored to use the new markers and direct assertions, improving overall code quality.

