---
title: "Feature: firewall"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/firewall/README.md
github_target_path: docs/reference/features/firewall.md
---

## Feature: firewall

### Description

Adds an `nftables`-based firewall to Garden Linux, controlled by systemd.

### What it does

Installs `nftables` and enables the `nftables` systemd service so that
firewall rules are applied at boot. The default ruleset allows only
established/related traffic and inbound SSH (TCP port 22); all outbound and
forwarded traffic is permitted. Rules are loaded from drop-in configuration
files under `/etc/nft.d/`, making it easy to extend the ruleset without
modifying the base configuration:

```
IPv4 and IPv6: /etc/nft.d/default.conf
```

Default policy summary:

| Direction | Default |
|---|---|
| Input | Drop (except TCP/22 and established/related) |
| Output | Accept |
| Forward | Accept |

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/firewall/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Enables the `nftables` systemd service and appends a drop-in include directive to `/etc/nftables.conf` so that files in `/etc/nft.d/` are loaded. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/firewall/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/firewall/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/firewall/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `nftables`. |
| [`file.include/etc/nft.d/default.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/firewall/file.include/etc/nft.d/default.conf) ([`file.include`](/reference/features/#file-include)) | Default nftables ruleset: drops inbound traffic except established/related connections and TCP port 22 (SSH). |

### Related features

This feature has no include or exclude relationships.

### Further reading

- [nftables documentation](https://wiki.nftables.org/)

## Related topics

<RelatedTopics />

