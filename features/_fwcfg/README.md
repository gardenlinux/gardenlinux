---
title: "Feature: _fwcfg"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_fwcfg/README.md
github_target_path: docs/reference/features/_fwcfg.md
---

## Feature: _fwcfg

### Description

Enables support for [QEMU `fw_cfg`](https://www.qemu.org/docs/master/specs/fw_cfg.html)-based user configuration scripts, allowing the hypervisor to inject configuration into the guest at boot time.

### What it does

`_fwcfg` installs a systemd service (`qemu-fw_cfg-script.service`) and a helper binary (`run-qemu-fw_cfg-script`). At boot, the service reads a script from the QEMU `fw_cfg` interface (the `opt/com.coreos/config` or a similarly configured key) and executes it inside the guest. This allows operators to pass per-instance configuration — such as network setup or user data — directly from the hypervisor without requiring a metadata service.

The `file.include.markers.yaml` links the installed files to test-coverage markers for automated verification.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fwcfg/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Configures the image at build time to enable the `fw_cfg` service. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fwcfg/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fwcfg/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`file.include/etc/systemd/system/qemu-fw_cfg-script.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fwcfg/file.include/etc/systemd/system/qemu-fw_cfg-script.service) ([`file.include`](/reference/features/#file-include)) | Systemd unit that reads a configuration script from the QEMU `fw_cfg` device and executes it at boot. |
| [`file.include/usr/bin/run-qemu-fw_cfg-script`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fwcfg/file.include/usr/bin/run-qemu-fw_cfg-script) ([`file.include`](/reference/features/#file-include)) | Binary or script that reads the payload from the `fw_cfg` interface and invokes it as a shell script. |

### Related features

This feature has no include or exclude relationships.

### Further reading

- [QEMU Firmware Configuration (`fw_cfg`)](https://www.qemu.org/docs/master/specs/fw_cfg.html)

## Related topics

<RelatedTopics />

