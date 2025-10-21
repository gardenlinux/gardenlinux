# 15. No Backports from Debian Stable in Garden Linux

Date: 2025-10-21

## Status

Accepted

## Context

Garden Linux is built from snapshots of Debian testing. There is a temptation to use backport packages from Debian stable to address missing features or security updates. However, backports from stable can introduce several issues:

- Backported packages from Debian stable may depend on older or incompatible libraries, which can cause build failures in the Debian testing-based build environment.
- Introducing backports can result in package downgrades. For example, if Garden Linux includes version `1.3.7` and the stable backport is `1.2.12~bpo1`, replacing the newer version would remove features and introduce regressions, even if the stable backport as a newer security fix. Instead, the fix should be backported to the version from testing by Garden Linux maintainers.
- Backported package versions often use a tilde (`~`) in their numbering (e.g., `1.1~bpo`). This affects dpkg's version comparison logic, making the backport appear older than the upstream version (`1.1~bpo` < `1.1`). As a result, the GLVD vulnerability tracker may incorrectly flag packages as vulnerable, even if they contain the necessary fixes.
- Using other non-tilde characters (such as `+` or `-`) in version numbers does not cause this issue, but backports from Debian stable consistently use the tilde.

## Decision

Garden Linux must not use backport packages from Debian stable. All packages should originate from Debian testing or be built specifically for Garden Linux to ensure compatibility and correct version tracking.

## Consequences

- Package stability and compatibility are maintained by avoiding mismatched dependencies.
- GLVD can accurately track vulnerabilities without false positives caused by tilde-versioned backports.
- Additional effort may be required to build or update packages not yet available in Debian testing, but this ensures a more reliable and secure system.
