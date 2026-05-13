---
title: "Feature: baremetal"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/baremetal/README.md
github_target_path: docs/reference/features/baremetal.md
---

## Feature: metal
### Description
<website-feature>
This platform feature creates an artifact for (bare) metal systems. It is just a plaform wrapper for the [`metal`](/reference/features/metal) feature.
</website-feature>

### Features
This feature creates a (bare) metal compatible image artifact as an `.iso` file and includes further metal related stuff like standard kernel, etc. that are required for physical components.


### Unit testing
This platform feature supports unit testing and is based on the `metal` fixture to validate the applied changes according its feature configuration.

### Meta
|||
|---|---|
|type|platform|
|artifact|`.raw`,`.qcow2`|
|included_features|`cloud`|
|excluded_features|None|
