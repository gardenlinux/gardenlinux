---
title: Semantic Versioning
description: How we Version Garden Linux Releases
order: 140
related_topics:
  - /explanation/release-hierarchy.md
  - /explanation/packaging.md
  - /explanation/repo-infrastructure.md
  - /explanation/os-releases.md
  - /explanation/semver.md
  - /how-to/packaging/backporting.md
  - /how-to/releases/apt-repos.md
  - /how-to/releases/os-releases.md
  - /reference/releases/release-lifecycle
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4705"
migration_stakeholder: "@tmangold, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/explanation/semver.md
github_target_path: docs/explanation/semver.md
---

# Semantic Versioning

Garden Linux uses semantic versioning with the format `MAJOR.MINOR.PATCH`:

- **MAJOR**: Representing the number of days passed since 31st of March 2020
- **MINOR**: Incremental number for patch releases (e.g., `0`, `1`, `2`, ...)
- **PATCH**: Always `0` for Garden Linux releases

Examples:

- `2150.0.0` - Major release based on Debian snapshot from day 2150 (2026-02-18)
- `2150.1.0` - First minor release for the 2150 major version
- `2150.2.0` - Second minor release for the 2150 major version

:::tip
Lookup the [ADR 0011: Garden Linux versioning](/reference/adr/0011-garden-linux-versioning.html) for the exact definition.
:::

:::info
Older Garden Linux versions (before 2016) used a different versioning scheme (e.g., `1443.2`, `1592.5`). The documentation covers both schemes where relevant.
:::

## Related topics

<RelatedTopics />
