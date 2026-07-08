---
title: Creating OS Releases
description: Complete guide to creating Garden Linux OS major and minor releases
order: 3
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
github_source_path: docs/how-to/releases/os-releases.md
github_target_path: docs/how-to/releases/os-releases.md
---

# Creating OS Releases

This guide explains how to create Garden Linux major and minor OS releases.

## Release hierarchy

Garden Linux uses a [three-tier release hierarchy](/explanation/release-hierarchy.md) to deliver a complete operating system.

This document is about the third tier, the [OS Releases](/explanation/os-releases) - where abstract package definitions become concrete, deployable operating system images distributed to end users.

## Understanding OS releases

Read the [OS Releases Explanation](/explanation/os-releases.md) to get familiar with the concepts for the Releases.

## Prerequisites

Before creating an OS release, ensure you have:

- Write access to the `gardenlinux/gardenlinux` repository
- `gh` and `gh` CLI tool installed and configured

## Phase 0: Preparation

### Step 1: Assessment of current state

Verify that the system is ready for a release. This means all tests pass and there are no blockers for the next major release in the release workflows. Also assessing possible backports is important.

**For Major Releases (on `main` branch):**

- Is the [nightly workflow](https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml) green on the **`main` branch**?

**For Minor Releases (on release `rel-*` branch):**

- Are there any important fixes or features that need to be backported from the `main` branch?

**Security and Quality:**

- Are there any critical or highly-rated issues that need to be addressed?
- Have recent CVEs been assessed for impact?

### Step 2: Check previous tiers

Be sure to have complete [Packaging](/how-to/packaging/) and [Created a APT Repository](/how-to/releases/apt-repos) before proceeding.

## Phase 1: Creating the release

### Step 1: Build Garden Linux OS

Once the APT repository is ready, we can build the OS images in tier three:

**Checkout or Create Release Branch:**

```bash
# For major releases, create a new release branch from main
git checkout main
git pull
git checkout -b rel-MAJOR
git push origin rel-MAJOR

# For minor releases, checkout the existing release branch
git checkout rel-MAJOR
git pull
```

**Update VERSION File:**

```bash
# Edit the VERSION file to contain the new version
echo "MAJOR.MINOR.0" > VERSION

# Example for minor release:
echo "2150.1.0" > VERSION

# Commit the change
git add VERSION
git commit -m "Bump version to MAJOR.MINOR.0"
git push origin rel-MAJOR
```

**Trigger Build Workflow:**

The build process varies depending on the Garden Linux version:

**For releases 2016.0.0 and later (using [SemVer](/reference/glossary.html#semver)):**

Use the [manual release workflow](https://github.com/gardenlinux/gardenlinux/actions/workflows/manual_release.yml):

```bash
# Using gh CLI:
gh workflow run "Build and publish a release" \
--ref rel-MAJOR \
-f target=release \
-f version=MAJOR.MINOR.0

# Example:
gh workflow run "Build and publish a release" \
--ref rel-2150 \
-f target=release \
-f version=2150.1.0
```

Or via the GitHub UI:

1. Go to [Actions → Build and publish a release](https://github.com/gardenlinux/gardenlinux/actions/workflows/manual_release.yml)
2. Click "Run workflow"
3. Select the `rel-MAJOR` branch
4. Set version to `MAJOR.MINOR.0`
5. Leave target `release`
6. Leave other parameters at defaults

**For older releases (1443, 1592 using non-SemVer):**

Use the [nightly workflow](https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml) with version parameter:

```bash
# Using gh CLI:
gh workflow run nightly.yml \
--ref rel-MAJOR \
-f version=MAJOR.MINOR

# Example for 1443:
gh workflow run nightly.yml \
--ref rel-1443 \
-f version=1443.3
```

**Monitor the Build:**

- Watch the workflow progress in GitHub Actions
- Verify all build jobs complete successfully
- Check that artifacts are published

### Step 2: Create GitHub release

After the build completes, create the official GitHub release page:

```bash
# Run from main branch (not the release branch!)
git checkout main

# Using gh CLI:
gh workflow run "release page" \
--ref main \
-f run_id=<BUILD-RUN-ID>
-f is_latest=true # if this is the latest major.minor.0 version

# Example:
gh workflow run "release page" \
--ref main \
-f run_id=23802291489 \
-f is_latest=true # if this is the latest major.minor.0 version
```

:::tip
Get the "Run ID" from the URL of the "Build and publish a release" workflow run, e.g. https://github.com/gardenlinux/gardenlinux/actions/runs/23802291489
:::

Or via the GitHub UI:

1. Go to [Actions → release page](https://github.com/gardenlinux/gardenlinux/actions/workflows/manual_gh_release_page.yml)
2. Click "Run workflow"
3. Select `main` branch
4. Set Build workflow run ID to `BUILD-RUN-ID` (e.g. `23802291489`)

:::warning
Always review the generated release notes before publishing, especially the "Changes" section.

The "Changes" section lists:

- Upgraded packages in the minor release
- Fixed CVEs

This data is generated by [glvd](https://github.com/gardenlinux/glvd) and may not be perfect. Verify:

- CVE fixes match your expectations
- Package upgrades are correctly listed
- No unexpected changes appear

:::

**Tag Manifest for Non-SemVer Releases:**

:::warning
For releases that do not use semantic versioning (e.g., `1877.5`), add an extra tag for compatibility with Gardener (especially for USI images).

```bash
# Example: Tag 1877.5 as 1877.5.0
oras tag ghcr.io/gardenlinux/gardenlinux:1877.5 1877.5.0
```

:::

### Step 3: [ONLY FOR MAJOR RELEASES] Create rel-MAJOR Branch in repo

:::danger
This step only applies to new major releases, not minor releases.
:::

Create a release branch in the `gardenlinux/repo` repository based on the new release tag:

```bash
cd /path/to/repo
git pull --tags
git checkout MAJOR.0.0
git checkout -b rel-MAJOR
git push -u origin rel-MAJOR
```

Example:

```bash
cd /path/to/repo
git pull --tags
git checkout 2150.0.0
git checkout -b rel-2150
git push -u origin rel-2150
```

This branch is used for creating future minor releases of the APT repository.

### Step 4: Generate CPE file

Generate the Common Platform Enumeration (CPE) file for the new release:

```bash
# Run from main branch
gh workflow run "Generate and upload CPE to a release" \
--ref main \
-f version=MAJOR.MINOR.0

# Example:
gh workflow run "Generate and upload CPE to a release" \
--ref main \
-f version=2150.1.0
```

Or via GitHub UI:

1. Go to [Actions → Generate and upload CPE](https://github.com/gardenlinux/gardenlinux/actions/workflows/cpe.yml)
2. Click "Run workflow"
3. Select `main` branch
4. Set version to `MAJOR.MINOR.0`

### Step 5: Update Garden Linux documentation

:::info
TODO: add steps on how to update the documentation
:::

## Phase 2: Post-release work

### Verify release completeness

- Verify the GitHub release page is complete and accurate
- Check that all expected artifacts are attached to the release
- Confirm the CPE file was generated and uploaded
- Test installation using the new release

### Notify stakeholders

- Notify relevant teams about the new release
- Gardener OS Extension Team
- Update any documentation referencing supported versions

## Related topics

<RelatedTopics />
