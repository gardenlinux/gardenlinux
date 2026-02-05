# 32. Garden Linux canonical name structure

Date: 2026-02-26

## Status

Draft

## Context

While Garden Linux canonical names (short `cname`) as a representation of flavors for specific architectures, versions and commits are commonly referred to an ADR is missing defining the parts of it. Historically the `cname` contains the platform, zero or more features, the architecture and version information. The platform and features part is referred to as "flavor".

## Decision

- `cname` contains exactly one platform as of [ADR 0020](0020-enforce-single-platform-by-default-in-builder.md) as long as it is not superseded.
- The platform should but do not have to be at the first position of the flavor string.
- Features are divided with `-`. `_` is used alternately as stated below.
- Feature flags are prefixed with `_`. The `-` is omitted in this case.
- Features are typically sorted by alphabet or a dependency and feature type based algorithm.
- All features combined form a "flavor".
- Appended to a "flavor" are in exact the following order, divided by a `-`:
  - Architecture
  - Semantic version string or `today` for local builds
  - Commit ID (currently configured as first eight characters of an Git commit hash) or `local` for local build
- Version information can be read from `COMMIT` and `VERSION` files of the `gardenlinux` Git repository to form the `cname` as described above.

## Consequences

- To ensure compatibility between tooling the `python-gardenlinux-lib` based tools should be used if applicable. The `python-gardenlinux-lib` contains unit-tests to ensure and conform to this ADR.
- Additional generators and parsers must ensure the structure and all parts mentioned in this ADR are provided in the correct order.
