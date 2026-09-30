---
title: "Feature: aide"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/aide/README.md
github_target_path: docs/reference/features/aide.md
---

## Feature: aide
### Description
<website-feature>
This feature installs the host-based intrusion detection system Aide.
</website-feature>

### Features
This feature installs the host-based intrusion detection system Aide and adds a configuration file for Aide, as well as the related systemd unit file that ensures to creates an Aide database. Aide is configured to runs every night.

### Unit testing
The related unit tests ensure that the needed packages are installed and the cron job will run nightly.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|None|
|excluded_features|None|
