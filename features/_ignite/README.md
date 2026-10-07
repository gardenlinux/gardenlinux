---
title: "Feature: _ignite"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_ignite/README.md
github_target_path: docs/reference/features/_ignite.md
---

## Feature: _ignite

### Description

Installs [Ignition](/reference/glossary#ignition) and integrates it into the initrd for declarative first-boot system configuration.

### What it does

`_ignite` installs the `ignition` package along with `dracut-network` and `curl`, and configures dracut to include Ignition in the initrd via `30-ignition.conf`. A custom dracut module (`30ignition-extra`) extends the upstream Ignition support with an environment variable generator (`ignition-env-generator.sh`), a static environment file (`ignition-files.env`), a `module-setup.sh` for module registration, and an `after-net-online.conf` ordering file that ensures Ignition runs after the network is available.

Ignition processes a JSON configuration fetched from a platform-specific source (such as a cloud metadata service or `fw_cfg`) to provision users, files, systemd units, and disks on first boot. Features such as [`_pxe`](/reference/features/_pxe) and [`_bfpxe`](/reference/features/_bfpxe) include `_ignite` to provide this capability.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ignite/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ignite/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ignite/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `dracut-network`, `ignition`, and `curl`. |
| [`file.include/etc/dracut.conf.d/30-ignition.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ignite/file.include/etc/dracut.conf.d/30-ignition.conf) ([`file.include`](/reference/features/#file-include)) | Tells dracut to include the Ignition module when building the initrd. |
| [`file.include/usr/lib/dracut/modules.d/30ignition-extra/after-net-online.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ignite/file.include/usr/lib/dracut/modules.d/30ignition-extra/after-net-online.conf) ([`file.include`](/reference/features/#file-include)) | Ordering configuration that ensures the Ignition-extra module activates after network connectivity is established. |
| [`file.include/usr/lib/dracut/modules.d/30ignition-extra/ignition-env-generator.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ignite/file.include/usr/lib/dracut/modules.d/30ignition-extra/ignition-env-generator.sh) ([`file.include`](/reference/features/#file-include)) | Systemd environment generator that exports Ignition platform and configuration URL variables in the initrd. |
| [`file.include/usr/lib/dracut/modules.d/30ignition-extra/ignition-files.env`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ignite/file.include/usr/lib/dracut/modules.d/30ignition-extra/ignition-files.env) ([`file.include`](/reference/features/#file-include)) | Static environment file with default Ignition settings included in the initrd. |
| [`file.include/usr/lib/dracut/modules.d/30ignition-extra/module-setup.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ignite/file.include/usr/lib/dracut/modules.d/30ignition-extra/module-setup.sh) ([`file.include`](/reference/features/#file-include)) | Registers the `30ignition-extra` dracut module and declares its dependencies. |

### Related features

This feature has no include or exclude relationships.

### Further reading

- [Ignition](https://coreos.github.io/ignition/)

## Related topics

<RelatedTopics />

