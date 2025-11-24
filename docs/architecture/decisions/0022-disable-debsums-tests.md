# 22. Disable Debsums Tests entirely

Date: 2025-11-24

## Status

Proposed

## Context

During migration of [test_debsums.py](../../../features/base/test/test_debsums.py) with issue #3785 to the test-ng framework, we found that the tests for debsums are skipped in the [cloud](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/test/debsums.disable), in [metal](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/test/debsums.disable) and on [container](https://github.com/gardenlinux/gardenlinux/blob/main/features/container/test/debsums.disable). 

Also the package `debsums` is not [included in the base image](../../../tests/helper/tests//debsums.py#6) and need to be installed or added to the base image. Installing the package would violate the decision to avoid installing packages in [ADR 0007](0007-non-invasive-read-only-testing.md).

The integrity of the base image should not be based on a single test on the package level.

## Decision

We do not migrate the debsum test case to the tests-ng.

## Consequences

Positive:
- We do not need to change the base image.
- Clean up on not necessary tests.

Negative:
- We do not check for changed base files on package level anymore.
