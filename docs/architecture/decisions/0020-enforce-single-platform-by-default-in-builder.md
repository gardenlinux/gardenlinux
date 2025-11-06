# 20. Enforce Single Platform by Default in Garden Linux Builder

Date: 2025-11-06

## Status

Accepted

## Context

Garden Linux builds are defined by a set of *features*, with `platform` being a special *feature* type. A recent regression in the manifest (starting with release `2032.0.0`) caused the `openstackbaremetal` flavor to have its platform set to `metal,openstackbaremetal` instead of just `openstackbaremetal`. This change silently broke the GLCI, resulting in OpenStack bare metal images being skipped and not published. The issue went unnoticed, affecting release `1877.6` (but not `1877.5`), which was published without bare metal flavors. This highlights the risk of allowing multiple platforms in a build and demonstrates the need for stricter enforcement to prevent silent failures and ensure reliable image publication.

## Decision

1. The builder will be changed so that, by default, it enforces the presence of exactly one platform feature in a build.

2. If zero or multiple platforms are specified, the build will fail.

3. The previous behavior (allowing multiple platforms) will remain available via an explicit opt-in flag.

## Consequences

- Multiple features in the `gardenlinux/gardenlinux` repo need to be changed.
- The builder needs to be changed (for example the `bootstrap` phase relies on the current behavior).
- Builds with zero or multiple platforms will fail unless the opt-in flag is used.
- The change will affect the "Common Name" (cname) of many image builds, as features like 'metal' will no longer be considered platforms. This impacts both command line arguments for the builder and output artifact filenames.
- This is a user-facing change and may cause issues for known and unknown users of the build infrastructure, requiring communication and migration support.
- Consumers relying on multiple platforms or cnames may be affected and need to update their workflows.
- The builder will support platform variants, requiring additional branching logic.
- Documentation and tooling must be updated to reflect the new enforcement and flag usage.
