---
title: "Install on STACKIT"
description: "STACKIT platform-specific installation and configuration tasks"
related_topics:
  - /tutorials/cloud/first-boot-stackit.md
  - /how-to/installation/post-install.md
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/installation/cloud/stackit.md
github_target_path: docs/how-to/installation/cloud/stackit.md
---

# Install on STACKIT

This guide covers platform-specific installation and configuration tasks for deploying Garden Linux on [STACKIT](https://www.stackit.de/), the cloud platform by Schwarz Group built on OpenStack.

::: tip New to STACKIT Deployments?

For a complete step-by-step first-boot walkthrough, see the [First Boot on STACKIT](/tutorials/cloud/first-boot-stackit.md) tutorial. The tutorial covers uploading an image, launching a server, configuring network access, and connecting via SSH.

:::

## Post-Installation Steps

After installation, follow one or more of these post-installation steps to complete your STACKIT setup:

- [Provision with cloud-init](/how-to/installation/cloud-init.md) — create users, install packages, and configure services on first boot

:::info STACKIT Default User
On STACKIT, cloud-init creates an `admin` user with passwordless `sudo` access via the `sudo` group (not `wheel`). This is configured in the STACKIT platform feature and does not require manual user creation.
:::

## Related topics

<RelatedTopics />
