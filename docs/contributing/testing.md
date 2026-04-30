---
title: "Testing Garden Linux"
description: Get started with the Garden Linux Testing Framework
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
github_source_path: docs/contributing/testing.md
github_target_path: docs/contributing/testing.md
---

# Testing Garden Linux

The Garden Linux test framework supports testing images in various environments including chroot, QEMU virtual machines, cloud providers, and OCI containers. This page provides navigation to all testing documentation organized by the Diátaxis framework.

## Understanding the Test Framework

Learn about the architecture and design of the Garden Linux test framework:

- [Test Framework Architecture](../explanation/testing/test-framework-architecture.md) - Framework design, plugins, handlers, and distribution system
- [Test Organization](../explanation/testing/test-organization.md) - How tests are structured and why

## Running Tests

Step-by-step guides for running and debugging tests:

- [Run Tests](../how-to/testing/run-tests.md) - Main guide for running tests in all environments
- [Setup Test Environment](../how-to/testing/setup-test-environment.md) - Prerequisites and installation
- [Debug Tests](../how-to/testing/debug-tests.md) - Troubleshooting and debugging workflows
- [Test in Cloud](../how-to/testing/test-in-cloud.md) - Cloud provider testing (AWS, Azure, GCP, ALI, OpenStack)

## Developing Tests

Complete reference documentation for test developers:

- [Developing Tests](../reference/testing/developing-tests.md) - Principles, best practices, and guidelines
- [Test Coverage Markers](../reference/testing/test-coverage-markers.md) - Coverage marker system and usage
- [CLI Reference](../reference/testing/test-cli.md) - Complete command-line interface reference

## Architecture Decisions

The Garden Linux test framework is built on several architectural decisions:

- [ADR-0006](../reference/adr/0006-new-test-framework-in-place-self-contained-test-execution.md) - Self-contained test execution
- [ADR-0007](../reference/adr/0007-non-invasive-read-only-testing.md) - Non-invasive testing
- [ADR-0032](../reference/adr/0032-static-feature-test-coverage-analysis.md) - Test coverage analysis

For more details, see [Test Framework Architecture](../explanation/testing/test-framework-architecture.md#related-architecture-decisions).

## Related Topics

<RelatedTopics />
