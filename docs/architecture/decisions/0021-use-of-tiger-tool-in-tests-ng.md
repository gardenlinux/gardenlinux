# 21. Use of tiger tool in tests-ng

Date: 2025-11-11

## Status

Proposed

## Context

While migrating server feature tests to the new framework, we need to take another look on certain decisions that were
made in the past. One such decision was the development of a test case based on the results of running of the tiger
security scanner. It's usefulness in the new test framework, however, is questionable.

The reasons are:

- this test relies on a [tool](https://github.com/gardenlinux/gardenlinux/blob/092f86bec6ab335d01d9f1cfeabcf4b4130ec42b/tests/helper/tests/tiger.py#L10)
that is currently not included in the tests-ng test runtime, which means that tiger package has to be integrated there;
this increases complexity of the test infrastructure
- moreover, the tiger test itself is configured to be [always skipped](https://github.com/gardenlinux/gardenlinux/blob/092f86bec6ab335d01d9f1cfeabcf4b4130ec42b/tests/helper/tests/tiger.py#L7)
(by using a combination of `provisioner_chroot` and `non_provisioner_chroot` fixtures): whether intentional or not,
this means that the test is not being used for at least [8 months](https://github.com/gardenlinux/gardenlinux/blame/092f86bec6ab335d01d9f1cfeabcf4b4130ec42b/tests/helper/tests/tiger.py#L7)

## Decision

The proposal is to NOT to migrate tiger test case to the tests-ng.

## Consequences

Positive: tests-ng test runtime is less complex, no need to maintain the test case which is not really used.

Negative: maybe we are losing some of the benefits security scanner like tiger could bring to the table.
