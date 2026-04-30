---
title: "Feature: cisSshd"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cisSshd/README.md
github_target_path: docs/reference/features/cisSshd.md
---

## Feature: cisSshd
### Description
<website-feature>

This subfeature manages the sshd configuration according to the CIS benchmarks. This features depends on its parents feature `cis`.
</website-feature>

### Features
This feature manages the sshd configuration and adjusts the used ciphers and defines a banner.

### Unit testing
Unit tests are only supported by its parent feature `cis`. See also [../cis/README.md](../cis/README.md).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|cis|
|excluded_features|None|
