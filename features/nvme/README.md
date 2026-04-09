---
title: "Feature: nvme"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/nvme/README.md
github_target_path: docs/reference/features/nvme.md
---

## Feature: nvme
### Description
<website-feature>
This feature installs nvme cli
</website-feature>

### Features
This feature installs nvm-cli as well as a systemd unit that creates /etc/nvme/hostnqn and /etc/nvme/hostid just as apt would after installing the package.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|multipath|
|excluded_features|None|
