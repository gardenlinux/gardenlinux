---
title: "Release Lifecycle"
description: "Garden Linux release lifecycle phases: standard maintenance, extended maintenance, and end of support."
order: 1
migration_status: "done"
migration_source: "00_introduction/release.md"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/releases/release-lifecycle.md
github_target_path: docs/reference/releases/release-lifecycle.md
---

# Release Lifecycle

Garden Linux follows a structured release process with predictable maintenance phases. This document explains the release lifecycle, maintenance commitments, and terminology.

For the current list of maintained releases, see [Maintained Releases](maintained-releases.md). For releases that have reached end of maintenance, see [Archived Releases](archived-releases.md).

## Stable Releases

Garden Linux publishes up to two stable releases per year, typically at six-month intervals. Each new major release introduces significant changes such as updated software packages or libraries. The initial major release establishes a frozen codebase that receives updates as minor versions during the one-year maintenance period.

Each stable release progresses through three maintenance phases:

### Standard Maintenance

Standard maintenance begins when a new stable release is published and continues for six months. During this phase, the Garden Linux team performs active maintenance including:

- Bug fixes
- Updates to newer minor versions of software packages
- Proactive monitoring and assessment of security vulnerabilities
- Performance improvements and enhancements

General best practice is to always use the latest minor version of the latest release.

### Extended Maintenance

Extended maintenance starts after the standard maintenance phase ends and continues for another six months. During this phase, only [Common Vulnerabilities and Exposures (CVE)](https://csrc.nist.gov/glossary/term/common_vulnerabilities_and_exposures) with high or critical severity (7.0-10.0) according to the [Common Vulnerability Scoring System (CVSS)](https://nvd.nist.gov/vuln-metrics) are patched. For more details, refer to the [Garden Linux Security Response Process](../../contributing/security.html).

This phase gives users sufficient time to plan and execute their transition to the latest release in standard maintenance.

### End of Maintenance

End of maintenance occurs one year after the initial stable release was published. After this date, no further planned maintenance activities are performed. Users can continue to use the stable release at their own risk.

Users can request an exceptional minor release via a GitHub issue in the [gardenlinux](https://github.com/gardenlinux/gardenlinux/issues/new/choose) repository. There is no guarantee that such requests will be fulfilled—maintainers reserve the right to reject requests and fix forward only in the latest stable release that is in standard maintenance. In exceptional situations (for example, a delay of the next planned release), the extended maintenance phase can be extended by up to six months.

## Minor Releases

During the maintenance period, updates are provided as minor releases (for example, "1592.1"). Minor releases are considered stable, and users are encouraged to always use the latest minor release of the latest stable major release.

Minor releases follow these rules:

- Can include higher minor versions of software packages or libraries already included in the stable release
- Can include security enhancements related to vulnerabilities identified after the release of the previous minor version
- Can remove software packages or libraries in rare exceptional situations (for example, due to security or legal risks identified after the release was published). Such changes are documented in the release notes

Before version 2017, minor releases were referred to as patch releases and used a two-number version format. See [Garden Linux Versioning](../adr/0011-garden-linux-versioning.md) for more information.

## Nightly Releases

Every night, a new build is triggered via the GitHub Action [Nightly Build](https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml). You can monitor build status on the action page. The maintainers aim for a successful build every 24 hours.

Occasionally, nightly patches (like "nightly-1592.1") are released if the initial nightly build requires urgent fixes.

Nightly releases contain the latest software packages and are geared toward rapid iteration for advanced users interested in cutting-edge changes. However, they are not as thoroughly maintained and tested as stable releases. Nightly releases do not include maintenance commitments and are not recommended for production environments.

Up to once per quarter, a nightly release is promoted to a stable release and is then supported with nine months of standard maintenance.

## Next Release

The "next" release is a projection of the upcoming stable release. It exists primarily to give users an idea of when the next stable version might be released and how long it might be supported.

See [Maintained Releases](maintained-releases.md) for the current list of planned and active releases.

## Dictionary

To ensure common understanding, the key terms used throughout this document are defined below:

- **Release**: The process of publishing a new stable version of the Garden Linux distribution
- **Standard maintenance**: The initial six-month window after the release of a new version of Garden Linux
- **Extended maintenance**: The six-month window following the end of standard maintenance
- **End of maintenance**: The date on which the extended maintenance ends and the release enters an unsupported state

## Further Reading

- [Maintained Releases](maintained-releases.md) — Currently supported Garden Linux releases
- [Archived Releases](archived-releases.md) — Releases past end of maintenance
- [Release Notes](release-notes/) — Detailed release-specific notes
