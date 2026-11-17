---
title: "Feature: checkbox"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/checkbox/README.md
github_target_path: docs/reference/features/checkbox.md
---

## Feature: checkbox

### Description

Integrates the [Canonical Checkbox hardware testing framework](https://github.com/canonical/checkbox) into a Garden Linux ISO for automated hardware qualification and test reporting.

### What it does

`checkbox` installs `checkbox-ng`, `checkbox-provider-base`, and `nginx`, then adds Garden Linux-specific Checkbox test units: a category definition, job definitions, a manifest, and a test plan. Several helper scripts run hardware-specific checks (TPM presence, hardware encryption, virtualization status, and dmesg color output). A `generate-report.service` systemd unit assembles a test report on boot, and `nginx` serves the report over HTTP.

The `exec.config` script configures the image for the Checkbox environment, and `file.include/etc/kernel/cmdline.iso` sets kernel parameters appropriate for an ISO boot used during hardware testing.

`checkbox` includes [`_iso`](/reference/features/_iso) because it is designed to boot from a live ISO on the hardware under test. It excludes features that are incompatible with the minimal, controlled testing environment: [`sap`](/reference/features/sap), [`firewall`](/reference/features/firewall), [`log`](/reference/features/log), [`_selinux`](/reference/features/_selinux), and [`_ignite`](/reference/features/_ignite).

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Configures the image at build time for the Checkbox test environment. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag`, included feature `_iso`, and excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `checkbox-ng`, `checkbox-provider-base`, and `nginx`. |
| [`file.include/etc/kernel/cmdline.iso`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/etc/kernel/cmdline.iso) ([`file.include`](/reference/features/#file-include)) | Kernel command line parameters used when booting the Checkbox ISO on the hardware under test. |
| [`file.include/etc/systemd/journald.conf.d/10-logs.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/etc/systemd/journald.conf.d/10-logs.conf) ([`file.include`](/reference/features/#file-include)) | Adjusts journald log retention settings to preserve test output for reporting. |
| [`file.include/etc/systemd/system/generate-report.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/etc/systemd/system/generate-report.service) ([`file.include`](/reference/features/#file-include)) | Systemd unit that runs the report generator after tests complete and places the HTML report in the nginx document root. |
| [`file.include/etc/systemd/system.conf.d/10-dmesg.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/etc/systemd/system.conf.d/10-dmesg.conf) ([`file.include`](/reference/features/#file-include)) | Configures systemd to capture dmesg output for inclusion in the test report. |
| [`file.include/usr/lib/checkbox-provider-base/bin/dmesg_colored.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/usr/lib/checkbox-provider-base/bin/dmesg_colored.sh) ([`file.include`](/reference/features/#file-include)) | Formats dmesg output with color coding for easier review in the test report. |
| [`file.include/usr/lib/checkbox-provider-base/bin/hw_encrypt_check.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/usr/lib/checkbox-provider-base/bin/hw_encrypt_check.sh) ([`file.include`](/reference/features/#file-include)) | Checks whether hardware encryption (such as self-encrypting drive support) is available. |
| [`file.include/usr/lib/checkbox-provider-base/bin/tpm_check.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/usr/lib/checkbox-provider-base/bin/tpm_check.sh) ([`file.include`](/reference/features/#file-include)) | Checks whether a Trusted Platform Module (TPM) is present and accessible. |
| [`file.include/usr/lib/checkbox-provider-base/bin/virtualization_disabled.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/usr/lib/checkbox-provider-base/bin/virtualization_disabled.sh) ([`file.include`](/reference/features/#file-include)) | Verifies that the system is running on bare metal rather than inside a virtual machine. |
| [`file.include/usr/local/bin/generate-report.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/usr/local/bin/generate-report.sh) ([`file.include`](/reference/features/#file-include)) | Script that aggregates Checkbox test results into a structured HTML report. |
| [`file.include/usr/share/checkbox-provider-base/units/gardenlinux/category.pxu`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/usr/share/checkbox-provider-base/units/gardenlinux/category.pxu) ([`file.include`](/reference/features/#file-include)) | Checkbox category definition grouping all Garden Linux hardware test jobs. |
| [`file.include/usr/share/checkbox-provider-base/units/gardenlinux/jobs.pxu`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/usr/share/checkbox-provider-base/units/gardenlinux/jobs.pxu) ([`file.include`](/reference/features/#file-include)) | Checkbox job definitions for individual Garden Linux hardware test cases. |
| [`file.include/usr/share/checkbox-provider-base/units/gardenlinux/manifest.pxu`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/usr/share/checkbox-provider-base/units/gardenlinux/manifest.pxu) ([`file.include`](/reference/features/#file-include)) | Checkbox manifest declaring hardware capabilities expected to be present on the device under test. |
| [`file.include/usr/share/checkbox-provider-base/units/gardenlinux/test-plan.pxu`](https://github.com/gardenlinux/gardenlinux/blob/main/features/checkbox/file.include/usr/share/checkbox-provider-base/units/gardenlinux/test-plan.pxu) ([`file.include`](/reference/features/#file-include)) | Checkbox test plan that selects and orders the Garden Linux jobs for a complete hardware qualification run. |

### Related features

**Includes:**

- [`_iso`](/reference/features/_iso) — Provides the live ISO boot environment required to run hardware tests from removable media.

**Excludes (incompatible with):**

- [`sap`](/reference/features/sap) — SAP-specific packages and configuration are not needed in the hardware test environment.
- [`firewall`](/reference/features/firewall) — Firewall rules could interfere with test network connectivity and report serving.
- [`log`](/reference/features/log) — Centralized log forwarding is unnecessary and may conflict with local log collection for test reports.
- [`_selinux`](/reference/features/_selinux) — SELinux mandatory access control may block test scripts from accessing hardware resources.
- [`_ignite`](/reference/features/_ignite) — Ignition first-boot configuration is not applicable to the hardware test ISO use case.

### Further reading

- [Canonical Checkbox hardware testing framework](https://github.com/canonical/checkbox)

## Related topics

<RelatedTopics />

