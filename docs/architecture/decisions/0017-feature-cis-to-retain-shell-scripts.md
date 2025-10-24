# 17. Retain Shell-Based CIS Implementation for tests-ng (No Custom Python Rewrite)

Date: 2025-10-24

## Status

Accepted

## Context

- This decision affects only the CIS tests in the new tests-ng framework, not CIS behavior in the runtime image itself.

 - Garden Linux’s CIS validation currently integrates upstream shell scripts from ovh/debian-cis. We need to clarify why we intentionally do not rewrite these tests into Python / pytest-based native test-ng modules.

## Key considerations:

 - Rewriting CIS test logic into native tests-ng Python tests would make Garden Linux fully responsible for maintaining evolving CIS rules.

 - Another consideration is the uniformity of tests in the new test framework. The (acceptable) downside of this decision is that the tests in the CIS feature don't follow our best practices for tests.

 - ovh/debian-cis is actively maintained upstream — following industry-standard CIS baseline updates.

 - We intentionally avoid duplicating upstream effort and introducing maintenance obligations that do not provide strategic value.

 - Our responsibility is limited to packaging, integrating, and executing upstream logic safely, not to reimplement or maintain CIS rule definitions.

 - To ensure architectural clarity and traceability, this is documented as a formal design decision (marker).

## Decision

Garden Linux, for tests-ng framework, will retain the upstream shell-based CIS implementation of tests without rewriting or owning the CIS logic internally as an Exception.
