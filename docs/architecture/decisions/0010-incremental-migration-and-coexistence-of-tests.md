# ADR 0010: Incremental Migration and Coexistence of Tests

**Date:** 2025-07-25

## Status

Accepted

## Context

The Garden Linux test framework is undergoing a major redesign to improve safety, portability, and maintainability. However, the existing framework is deeply integrated into current workflows and contains a large number of tests and helper functions. A complete, immediate rewrite ("big bang" migration) would be risky, disruptive, and could block ongoing development and validation work. There is a need to balance progress on the new framework with continuity for existing users and processes.

Key considerations:
- **Risk of Disruption:** A full rewrite could introduce regressions, break existing workflows, and delay feature delivery.
- **Audit and Refactoring Effort:** Many existing tests require review and adaptation to meet new requirements (e.g., read-only, in-place execution).
- **Parallel Development:** Teams may need to maintain and run both frameworks during the transition period.

## Decision

We will adopt an incremental migration strategy for the test framework redesign:

- **Coexistence:** The legacy and new test frameworks will be maintained in parallel, allowing tests to be ported and validated one by one.
- **Gradual Refactoring:** Tests and helpers will be audited and refactored incrementally to comply with new architectural principles (read-only, in-place, declarative logic).
- **Early Value:** New features and improvements will be delivered as soon as they are ready, without waiting for a complete migration.
- **Feedback Loops:** The migration process will incorporate feedback from users and maintainers to guide priorities and address issues as they arise.

## Consequences

- **Reduced Risk:** The migration avoids large-scale disruption and enables ongoing validation and feature delivery.
- **Continuous Improvement:** Teams can improve test quality and architecture over time, rather than all at once.
- **Operational Flexibility:** Both frameworks can be used as needed, ensuring coverage and compatibility during the transition.
- **Migration Overhead:** Some duplication of effort and maintenance will be required until the migration is complete.
