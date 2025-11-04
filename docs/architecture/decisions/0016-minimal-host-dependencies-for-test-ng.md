# 16. Avoid Host Dependency on `retry` Command in Makefile for tests-ng

Date: 2025-10-22

## Status

Accepted

## Context

Pull request [#3571](https://github.com/gardenlinux/gardenlinux/issues/3571) introduced a dependency on the `retry` command tool for the entire tests-ng build system. While this dependency is acceptable within self-containerizing build scripts and arguably tolerable in the run cloud script (which already requires various host tools for opentofu), it is undesirable in the Makefile. Increasing host dependencies in the Makefile leads to dependency creep, making builds less portable and harder to maintain.

## Decision

We will remove the direct dependency on the `retry` command from the Makefile for tests-ng. Instead, retry logic should be handled externally, such as by configuring the GitHub Action workflow to manage retries. This keeps the Makefile lean and minimizes host requirements.

## Consequences

- The Makefile for tests-ng will no longer require the `retry` command to be present on the host.
- Retry logic will be managed by the CI/CD pipeline (e.g., GitHub Actions), improving portability and maintainability.
- Host dependency creep is reduced, aligning with Garden Linux's goal of minimal host requirements for builds.
