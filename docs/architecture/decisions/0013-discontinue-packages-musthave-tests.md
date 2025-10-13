# 13. Discontinue `packages_musthave` tests

Date: 2025-10-09

## Status

Accepted

## Context

We are currently migrating from the old feature oriented test framework to a new independent test framework, where all test related files are stored in a separate directory. This results in better readability and should also make clear which issues a test is about. 
In the old framework, `test_packages_musthave.py` checks if all packages contained in the feature's `pkg.include` and not contained in a `pkg.exclude` of any feature of the flavor is installed. It only includes one line which is an import from a helper file.

## Decision

The `packages_musthave` will not be migrated to the new test framework:

- As the `packages_musthave` test uses `pkg.include` and `pkg.exclude` files of the currently used repository, the tests are not version independent
    - The new test framework is capable of testing production systems, which may be built with an older version of a feature than the test framework and may have fewer or other packages in that version, which would fail the test unintentionally
- The test only has low value, e.g. detecting misspelled or incomplete package names
- If a package is not found, the build will already fail
- Important packages can be checked in the feature test
- If a real value is found, the implementation from #3621 could be used

## Consequences

- It is no longer checked if all included packages are installed
- The test distribution artifact does not need to contain the package lists
- The tests have less potential incompatibilities between versions (different commit between image build and test distribution build)
