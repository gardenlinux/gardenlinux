---
title: "ADR 0039: Use the Latest GitHub-Hosted Ubuntu Runner Images"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/adr/0039-github-runner-images.md
github_target_path: docs/reference/adr/0039-github-runner-images.md
---

# ADR 0039: Use the Latest GitHub-Hosted Ubuntu Runner Images

Date: 2026-11-05

## Status

Accepted

## Context

GitHub announced the general availability of Ubuntu 26.04 and the migration of the `ubuntu-latest` label ([GitHub changelog](https://github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration)). The runner images used by Garden Linux workflows are currently a mix of `ubuntu-24.04`, `ubuntu-latest`, `ubuntu-slim`, and versioned ARM64 images. This inconsistency is spread across multiple repositories in the `gardenlinux` organisation, so the same runner migration has to be handled differently in each repository.

Pinning workflows to a named Ubuntu version such as `ubuntu-26.04` was considered, but it only moves the problem: GitHub decides when a runner image is deprecated and when `ubuntu-latest` moves on. A pinned version therefore creates a future point in time at which Garden Linux is forced to switch, independent of the project's own schedule.

The alternative is to always use the latest Ubuntu image GitHub provides. This surfaces incompatibilities as soon as GitHub changes the image, while the change is still small and can be fixed incrementally. The trade-off is reduced reproducibility of CI runs and the need to react quickly when an upstream image change breaks a workflow. If an error is not fixable right away an older image can be pinned on a per workflow or even job basis.

## Decision

All Linux jobs in `gardenlinux` organisation repositories use the latest [GitHub-hosted](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) Ubuntu runner available:

- x86_64 jobs use `ubuntu-latest`.
- ARM64 jobs use the latest available versioned ARM64 image, currently `ubuntu-26.04-arm`. This image is bumped to the next versioned ARM64 image when GitHub publishes it. The reason for this is, that there is no `ubuntu-latest-arm` label officially provided by GitHub.
- `ubuntu-slim` and other special-purpose or fixed-version Ubuntu runner labels are not used.

We do not pin a named Ubuntu version to delay a migration. If a job cannot run on the latest image, an exception must be documented alongside the code, together with the reason and a plan to remove the exception.

Existing workflows are migrated repository by repository. All still active release branches need to be migrated, too.

## Consequences

Positive:

- There is no GitHub-imposed cutover date at which a large migration must happen.
- Upstream image changes are detected early and can be fixed incrementally.
- All repositories follow one consistent runner policy.
- The recurring effort of migrating every repository separately is replaced by reacting to individual failures.

Negative:

- Runner environments are not strictly reproducible across time. However, this is inherent to GitHub-hosted
  runners in general: even version-pinned runners (e.g. `ubuntu-24.04`) receive rolling daily/weekly software
  updates from GitHub, meaning pinning does not yield real reproducibility.
- Upstream changes can break workflows at any time and require a timely reaction.
- ARM64 images have no `-latest` label, so the versioned image must still be updated manually. ARM64 images are used sparsely, so this is not big issue.

Mitigations:

- Garden Linux build infrastructure is designed to isolate builds from the host runner: build workloads
  execute inside controlled containers, chroots, or VMs rather than relying on mutable runner host packages.
- GitHub Actions remain pinned to full commit SHAs as decided in [ADR 0028](./0028-pin-actions-to-sha.md).
- Tool and dependency versions are pinned where reproducibility matters.
- Runner image changes only affect CI; they do not change the Garden Linux images produced by the build.

## Alternatives Considered

- **Pin `ubuntu-26.04`**: Rejected. It defers the migration instead of removing it and leaves the switch date under GitHub's control.
- **Keep the current mix of runner labels**: Rejected. It is inconsistent across repositories and makes failures harder to predict and fix.
- **Keep `ubuntu-slim` for lightweight jobs**: Rejected in favour of a unified runner policy.
- **Self-hosted or containerised runners**: Out of scope for this decision.

## References

- [Issue #5531: update github runner images to `ubuntu-latest`](https://github.com/gardenlinux/gardenlinux/issues/5531)
- [GitHub changelog: Ubuntu 26 generally available and `ubuntu-latest` migration](https://github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration)
- [GitHub-hosted runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [ADR 0028: Pinning All GitHub Actions in Garden Linux Workflows](./0028-pin-actions-to-sha.md)
