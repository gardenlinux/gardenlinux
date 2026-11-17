---
title: "Feature: _debug"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_debug/README.md
github_target_path: docs/reference/features/_debug.md
---

## Feature: _debug

### Description

Adds a debug container to the image that provides a writable environment for inspecting an otherwise immutable system.

### What it does

`_debug` installs `containerd` and `docker.io` along with a script (`setup-debugbox-ssh`) that creates and starts a debug container on the host. By default, the container is based on a Debian slim image with `openssh-server` installed and `sshd` running on port 22, giving SSH access to a writable environment that shares the host network and mounts host system directories.

Two systemd services are installed to create and start the container at boot time. The behavior is controlled by `/etc/debugbox.conf`:

- `IMAGE` — name of the local image (default: `debugbox`)
- `REGISTRY` — optional external registry to pull from
- `CONTAINER_ARCHIVE` — optional path to a local container archive
- `CMD` — command to run in the container (default: `/usr/sbin/sshd -D`)

The debug container can also be started from a local archive or pulled from an external registry, in which case the container is used as-is without modification.

:::warning
Do not use this feature in production images. The exposed ssh server imposes a security thread.
:::

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_debug/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Configures the image at build time to enable the debug container services. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_debug/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_debug/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `containerd` and `docker.io` to support running the debug container. |
| [`file.include/etc/debugbox.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_debug/file.include/etc/debugbox.conf) ([`file.include`](/reference/features/#file-include)) | Configuration file for the debug container, controlling the image source, registry, and command. |
| [`file.include/etc/systemd/system/setup-debugbox-ssh.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_debug/file.include/etc/systemd/system/setup-debugbox-ssh.service) ([`file.include`](/reference/features/#file-include)) | Systemd unit that creates and configures the debug container at boot time. |
| [`file.include/etc/systemd/system/ssh-container.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_debug/file.include/etc/systemd/system/ssh-container.service) ([`file.include`](/reference/features/#file-include)) | Systemd unit that starts the debug container and keeps it running. |
| [`file.include/usr/sbin/setup-debugbox-ssh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_debug/file.include/usr/sbin/setup-debugbox-ssh) ([`file.include`](/reference/features/#file-include)) | Script that pulls or loads the container image, installs `openssh-server` if needed, and starts `sshd`. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

