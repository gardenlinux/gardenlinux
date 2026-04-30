---
title: "Feature: cisPackages"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cisPackages/README.md
github_target_path: docs/reference/features/cisPackages.md
---

## Feature: cisPackages
### Description
<website-feature>

This subfeature manages the required and unwanted packages from the distribution repository. This features depends on its parents feature `cis`.
</website-feature>

### Features
This feature installs needed packages as well as it removes unwanted packages.

The following packages are installed:
* git
* syslog-ng
* libpam-pwquality
* tcpd

### Unit testing
Unit tests are only supported by its parent feature `cis`. See also [../cis/README.md](../cis/README.md).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|cis|
|excluded_features|None|
