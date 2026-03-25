---
title: "ADR 0025: Disable Debsums Tests entirely"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/adr/0025-disable-debsums-tests.md
github_target_path: docs/reference/adr/0025-disable-debsums-tests.md
---

# ADR 0025: Disable Debsums Tests entirely

Date: 2025-11-24

## Status

Proposed

## Context

During migration of [test_debsums.py](https://github.com/gardenlinux/gardenlinux/blob/5236b48f319b4f3b1d38e8631d6cb5d888623db0/features/base/test/test_debsums.py) with issue #3785 to the test-ng framework, we found that the tests for debsums are skipped in the [cloud](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/test/debsums.disable), in [metal](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/test/debsums.disable) and on [container](https://github.com/gardenlinux/gardenlinux/blob/main/features/container/test/debsums.disable). 

Also the package `debsums` is not [included in the base image](https://github.com/gardenlinux/gardenlinux/blob/5236b48f319b4f3b1d38e8631d6cb5d888623db0/tests/helper/tests/debsums.py#L6) and need to be installed or added to the base image. Installing the package would violate the decision to avoid installing packages in [ADR 0007](0007-non-invasive-read-only-testing.md).

The integrity of the base image should not be based on a single test on the package level.

## Decision

We do not migrate the debsum test case to the tests-ng.

## Consequences

Positive:
- We do not need to change the base image.
- Clean up on not necessary tests.

Negative:
- We do not check for changed base files on package level anymore.
