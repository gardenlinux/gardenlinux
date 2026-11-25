---
title: "Release Lifecycle"
description: "Garden Linux release lifecycle phases: standard maintenance, extended maintenance, long-term support (LTS), and end of support."
order: 1
related_topics:
  - /reference/releases/release-lifecycle
  - /reference/releases/maintained-releases
  - /reference/releases/archived-releases
  - /reference/releases/release-notes/
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/releases/release-lifecycle.md
github_target_path: docs/reference/releases/release-lifecycle.md
---

# Release Lifecycle

Garden Linux follows a structured release process with predictable maintenance phases. This document explains the release lifecycle, maintenance commitments, and terminology.

For the current list of maintained releases, see [Maintained Releases](maintained-releases.md). For releases that have reached end of maintenance, see [Archived Releases](archived-releases.md).

## Stable releases

Garden Linux publishes up to two stable releases per year, typically at six-month intervals. Each new major release introduces significant changes such as updated software packages or libraries. The initial major release establishes a frozen codebase that receives updates as minor versions during the maintenance period.

Most stable releases progress through three maintenance phases, described below. In addition, selected stable releases are designated as long-term support (LTS) releases, which follow the same phases but receive a significantly longer support window.

### Standard maintenance

Standard maintenance begins when a new stable release is published and continues for nine months. During this phase, the Garden Linux team performs active maintenance including:

- Bug fixes
- Updates to newer minor versions of software packages
- Proactive monitoring and assessment of security vulnerabilities
- Performance improvements and enhancements

General best practice is to always use the latest minor version of the latest release.

### Extended maintenance

Extended maintenance starts after the nine-month standard maintenance phase ends and continues for another six months. During this phase, only [Common Vulnerabilities and Exposures (CVE)](https://csrc.nist.gov/glossary/term/common_vulnerabilities_and_exposures) with high or critical severity (7.0-10.0) according to the [Common Vulnerability Scoring System (CVSS)](https://nvd.nist.gov/vuln-metrics) are patched. For more details, refer to the [Garden Linux Security Response Process](../../contributing/security.html).

This phase gives users sufficient time to plan and execute their transition to the latest release in standard maintenance.

### End of maintenance

End of maintenance occurs fifteen months after the initial stable release was published, aligned to the end of that month. After this date, no further planned maintenance activities are performed. Users can continue to use the stable release at their own risk.

Users can request an exceptional minor release via a GitHub issue in the [gardenlinux](https://github.com/gardenlinux/gardenlinux/issues/new/choose) repository. There is no guarantee that such requests will be fulfilled—maintainers reserve the right to reject requests and fix forward only in the latest stable release that is in standard maintenance. In exceptional situations (for example, a delay of the next planned release), the extended maintenance phase can be extended by up to six months.

### Long-term support (LTS)

Selected stable releases are designated as long-term support (LTS) releases. LTS releases go through the same standard and extended maintenance phases as other stable releases, but they receive a significantly longer support window.

Instead of reaching end of maintenance fifteen months after publication, an LTS release is maintained for five years (60 month) from its initial release date, aligned to the end of that month. Throughout this period the same maintenance rules apply: active maintenance during standard maintenance, followed by security-only fixes during extended maintenance.

Not every release is an LTS release. For the current list of maintained releases, including which ones are long-term supported, see [Maintained Releases](maintained-releases.md).

## Minor releases

During the maintenance period, updates are provided as minor releases (for example, "1592.1"). Minor releases are considered stable, and users are encouraged to always use the latest minor release of the latest stable major release.

Minor releases follow these rules:

- Can include higher minor versions of software packages or libraries already included in the stable release
- Can include security enhancements related to vulnerabilities identified after the release of the previous minor version
- Can remove software packages or libraries in rare exceptional situations (for example, due to security or legal risks identified after the release was published). Such changes are documented in the release notes

Before version 2017, minor releases were referred to as patch releases and used a two-number version format. See [Garden Linux Versioning](../adr/0011-garden-linux-versioning.md) for more information.

## Nightly releases

Every night, a new build is triggered via the GitHub Action [Nightly Build](https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml). You can monitor build status on the action page. The maintainers aim for a successful build every 24 hours.

Occasionally, nightly patches (like "nightly-1592.1") are released if the initial nightly build requires urgent fixes.

Nightly releases contain the latest software packages and are geared toward rapid iteration for advanced users interested in latest changes. However, they are not as thoroughly maintained and tested as stable releases. Nightly releases do not include maintenance commitments and are not recommended for production environments.

Up to once per quarter, a nightly release is promoted to a stable release and is then supported with nine months of standard maintenance.

## Next release

The "next" release is a projection of the upcoming stable release. It exists primarily to give users an idea of when the next stable version might be released and how long it might be supported.

See [Maintained Releases](maintained-releases.md) for the current list of planned and active releases.

## Dictionary

To ensure common understanding, the key terms used throughout this document are defined below:

- **Release**: The process of publishing a new stable version of the Garden Linux distribution
- **Standard maintenance**: The initial nine-month window after the release of a new version of Garden Linux
- **Extended maintenance**: The six-month window following the end of standard maintenance
- **End of maintenance**: The date on which the extended maintenance ends and the release enters an unsupported state. This is fifteen month after the release date.
- **Long-term support (LTS)**: A designated stable release that is maintained for five years, instead of the standard fifteen-month maintenance window

## Related topics

<RelatedTopics />
