# 28. Pinning All GitHub Actions in Garden Linux Workflows

Date: 2025-11-09

## Status

Accepted

## Context

GitHub Actions is a widely used CI/CD platform, but its package management model lacks several security features found in mature ecosystems. Notably, it does not support lockfiles, integrity hashes, or full dependency tree visibility. Mutable tags (e.g., `actions/checkout@v4`) can be retagged, causing workflows to silently run different code over time. Transitive dependencies are opaque and unpinned, and there is no built-in mechanism to verify the integrity of downloaded actions. Research has shown that most workflows execute unverified third-party code, and vulnerabilities in transitive dependencies are common. While GitHub has introduced mitigations like immutable releases and SHA pinning, these only partially address the risks.

For more background, see [Andrew Nesbitt's blog post](https://nesbitt.io/2025/12/06/github-actions-package-manager) and related research.

Garden Linux workflows already leverage Dependabot to manage GitHub Actions dependencies, including those referenced by commit SHA. Additionally, GitHub provides a repository setting to enforce the use of full-length commit SHAs for all actions. Enabling this setting ensures that workflows cannot use mutable tags and must specify exact commits.

## Decision

All GitHub Actions used in Garden Linux workflows must be pinned to a specific commit SHA, not just a version tag. This applies to both first-party and third-party actions.

We enable the 'Require actions to be pinned to a full-length commit SHA' setting for the `gardenlinux/gardenlinux` repo.

## Consequences

- Workflows will be more resistant to supply chain attacks and accidental breakage due to upstream changes.
- Reproducibility of CI runs will improve, as the same code will be executed on every run.
- Some risks remain, as transitive dependencies within composite actions may still be mutable and unpinned.
- The team should periodically review workflows for new best practices and tooling improvements in the GitHub Actions ecosystem.
