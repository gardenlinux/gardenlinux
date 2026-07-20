---
title: "Installation"
related_topics:
  - /tutorials/cloud/index.md
  - /tutorials/local/index.md
  - /tutorials/on-premises/index.md
  - /tutorials/container/index.md
  - /how-to/installation/post-install.md
  - /how-to/installation/cloud-init.md
  - /how-to/installation/ignition.md
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4623"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/installation/index.md
github_target_path: docs/how-to/installation/index.md
---

# Installation

Garden Linux runs on multiple platforms including cloud providers (AWS, Azure, GCP, OpenStack), local virtualization (KVM, Lima), bare-metal and on-premises infrastructure, and as OCI containers. Each installation category below contains platform-specific guides for deploying and configuring Garden Linux.

These how-to guides are task-oriented and assume familiarity with the basics. If you're new to Garden Linux or want a complete step-by-step walkthrough for your first deployment, start with the tutorials instead.

::: tip New to Garden Linux? Start with a Tutorial

For detailed step-by-step first-boot guides, see:

**Cloud Platforms:**
- [First Boot on AWS](/tutorials/cloud/first-boot-aws.md)
- [First Boot on Azure](/tutorials/cloud/first-boot-azure.md)
- [First Boot on GCP](/tutorials/cloud/first-boot-gcp.md)
- [First Boot on OpenStack](/tutorials/cloud/first-boot-openstack.md)

**Local Virtualization:**
- [First Boot on KVM](/tutorials/local/first-boot-kvm.md)
- [First Boot on Lima](/tutorials/local/first-boot-lima.md)

**On-Premises:**
- [First Boot on Bare Metal](/tutorials/on-premises/first-boot-bare-metal.md)

**Containers:**
- [First Boot as OCI Container](/tutorials/container/first-boot-oci.md)

:::

After installation, review the [Post Installation Steps](/how-to/installation/post-install.md) for user creation, SSH setup, and other initial configuration tasks.

## Provisioning and Configuration

Automate first-boot system configuration using declarative provisioning tools:

- **[Provision with cloud-init](/how-to/installation/cloud-init.md)** — Standard provisioning for cloud platforms (AWS, Azure, GCP, OpenStack)
- **[Provision with Ignition](/how-to/installation/ignition.md)** — First-boot provisioning for bare-metal and PXE deployments

These tools configure users, SSH keys, network settings, files, and systemd services automatically on first boot, eliminating manual post-installation steps.

<SectionIndex />

## Related topics

<RelatedTopics />
