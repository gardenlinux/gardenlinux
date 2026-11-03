---
title: "Feature: log"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/log/README.md
github_target_path: docs/reference/features/log.md
---

## Feature: log

### Description

Provides logging infrastructure including `auditd`, remote logging via `rsyslog-relp`, and `systemd-journal-remote`.

### What it does

Installs `auditd`, `rsyslog-relp`, and `systemd-journal-remote`. Configures `rsyslog` for structured logging and provides a base set of audit rules. Journal configuration is tuned for minimal footprint. Several rsyslog configurations are shipped as `.disabled` files that can be activated as needed.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Enables `auditd` and `rsyslog` services. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`file.include.stat`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include.stat) ([ref](/reference/features/#file-include-stat)) | Sets file ownership and permissions for log configuration files. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `auditd`, `systemd-journal-remote`, `rsyslog-relp`. |
| [`file.include/etc/rsyslog.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/rsyslog.conf) ([`file.include`](/reference/features/#file-include)) | Main rsyslog configuration file. |
| [`file.include/etc/audit/rules.d/10-base-config.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/audit/rules.d/10-base-config.rules) ([`file.include`](/reference/features/#file-include)) | Base auditd configuration rules applied to all systems. |
| [`file.include/etc/audit/rules.d/12-cont-fail.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/audit/rules.d/12-cont-fail.rules) ([`file.include`](/reference/features/#file-include)) | Audit rule to continue processing when a rule fails to load. |
| [`file.include/etc/audit/rules.d/12-ignore-error.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/audit/rules.d/12-ignore-error.rules) ([`file.include`](/reference/features/#file-include)) | Audit rule to suppress certain expected errors from the audit log. |
| [`file.include/etc/audit/rules.d/README`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/audit/rules.d/README) ([`file.include`](/reference/features/#file-include)) | Documentation for the audit rules directory and rule ordering conventions. |
| [`file.include/etc/rsyslog.d/10-local.conf.disabled`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/rsyslog.d/10-local.conf.disabled) ([`file.include`](/reference/features/#file-include)) | Template for local rsyslog output (disabled by default; rename to `.conf` to activate). |
| [`file.include/etc/rsyslog.d/20-input.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/rsyslog.d/20-input.conf) ([`file.include`](/reference/features/#file-include)) | rsyslog input module configuration. |
| [`file.include/etc/rsyslog.d/21-input-klog.conf.disabled`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/rsyslog.d/21-input-klog.conf.disabled) ([`file.include`](/reference/features/#file-include)) | Kernel log input for rsyslog (disabled by default). |
| [`file.include/etc/rsyslog.d/29-input-mark.conf.disabled`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/rsyslog.d/29-input-mark.conf.disabled) ([`file.include`](/reference/features/#file-include)) | Periodic log mark for rsyslog (disabled by default). |
| [`file.include/etc/rsyslog.d/30-server.conf.disabled`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/rsyslog.d/30-server.conf.disabled) ([`file.include`](/reference/features/#file-include)) | Remote server output template for rsyslog (disabled by default). |
| [`file.include/etc/rsyslog.d/60-audit-log-service.conf.disabled`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/rsyslog.d/60-audit-log-service.conf.disabled) ([`file.include`](/reference/features/#file-include)) | Audit log forwarding configuration for rsyslog (disabled by default). |
| [`file.include/etc/systemd/journald.conf.d/10-minimum.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/systemd/journald.conf.d/10-minimum.conf) ([`file.include`](/reference/features/#file-include)) | Sets minimum systemd journal configuration for a small footprint. |
| [`file.include/etc/systemd/journald.conf.d/20-rsyslog.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/log/file.include/etc/systemd/journald.conf.d/20-rsyslog.conf) ([`file.include`](/reference/features/#file-include)) | Configures rsyslog as a consumer of the systemd journal. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

