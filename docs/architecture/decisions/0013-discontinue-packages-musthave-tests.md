# 13. Discontinue `packages_musthave` tests

Date: 2025-10-09

## Status

Accepted

## Context

`test_packages_musthave.py` checks if all packages contained in the feature's `pkg.include` and not contained in a `pkg.exclude` of any feature of the flavor is installed.

## Decision

The `packages_musthave` will not be migrated to the new test framework:

- As the `packages_musthave` test uses `pkg.include` and `pkg.exclude` files of the currently used repository, the tests are not version independant
    - The new test framework is capable of testing production systems, which may have older versions
- The test only has low value, e.g. detecting misspelled or incomplete package names
- Important packages can be checked in the feature test
- If a real value is found, the implementation from #3621 could be used

## Consequences

- It is no longer checked if all included packages are installed
