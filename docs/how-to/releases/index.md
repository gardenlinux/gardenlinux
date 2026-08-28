---
title: "Releases"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/releases/index.md
github_target_path: docs/how-to/releases/index.md
---

# Releases

These pages explain how to create complete Garden Linux major and minor releases.

## Release hierarchy

Garden Linux uses a [three-tier release hierarchy](/explanation/release-hierarchy.md)
to deliver a complete operating system. Each tier depends on the previous one:

1. **[Package Releases](/how-to/releases/package-releases)** –
   Build and version individual software packages in `package-*` repositories.

2. **[APT Repository Releases](/how-to/releases/apt-repos)** –
   Assemble packages into an APT repository that OS images consume.

3. **[OS Releases](/how-to/releases/os-releases)** –
   Build complete, deployable operating system images from the APT repository.

Work through all three tiers in order to complete a release.

<SectionIndex />
