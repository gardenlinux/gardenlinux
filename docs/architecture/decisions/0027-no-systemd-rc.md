# 27. Do not use systemd release candidates

Date: 2025-12-05

## Status

Accepted

## Context

Starting with systemd v258, the release candidates migrated to testing in Debian have consistently broken our nightlies and also the SCI nightly builds because of various issues.
As systemd is an important component of Garden Linux, it would be prudent to skip the build of GL systemd packages based on upstream Debian rc versions to minimize the issues we might encounter; also, given the extra time till a non rc version is released, different dependent packages can also be brought up to date and have possible issues fixed e.g. dracut.

## Decision

We do not build systemd packages based on release candidates, not even for nightly releases. 

## Consequences

Positive:
- Fewer issues
- The package build is still rolling and the packages will get automatically built when a non rc version is released.
