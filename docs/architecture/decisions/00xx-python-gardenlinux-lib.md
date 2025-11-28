# xx. Organizing Python Code for Garden Linux

Date: 2025-11-28

## Status

Proposed

## Context

Historically, Python code for Garden Linux resided in the main repository, often without proper testing or organization. Some scripts were embedded directly in GitHub Actions workflows, while others were placed in the `hack/` directory. Dependency management for this code was inconsistent and lacked a systematic approach.

Recently, a separate repository, `python-gardenlinux-lib`, was introduced to host Python code for various usages. The work done to implement this separation brought benefits such as dedicated tests and linters, but these improvements are not inherently tied to having a separate repository.

Currently, the lib repo contains code used in GitHub Actions workflows and feature-related logic. This introduces an indirection, making debugging and modifying pipeline code more complex, as changes require updates in the lib repo, releasing a new version, and then updating the dependency in the main repo.

Examples for scope creep in the lib:

- [exportLibs.py](https://github.com/gardenlinux/python-gardenlinux-lib/pull/253)
- [release-notes](https://github.com/gardenlinux/python-gardenlinux-lib/tree/main/src/gardenlinux/github/release_notes)

## Decision

- Retain the `python-gardenlinux-lib` repository, but limit its scope to true library code, such as interfacing with OCI registries, parsing features, and generating cnames.
  - Exact decisions on individual code files and directories need to be made on a case-by-case basis, considering the following:
    - Does the code have more than one (potential) consumer?
    - Does leaving the code in the lib force the pipelines to install the lib?
- Move pipeline and feature-related Python code back into the main Garden Linux repository.
- Continue to maintain tests and linters for all Python code, regardless of its location.
- Introduce rules for where to place python code in the main repo, how to track dependencies and implement tests.
- Introduce a PR template for the lib to remind of above criteria to critically reflect if the code should go into the library.

## Consequences

- The library repo will be focused on reusable, generic components.
- Pipeline and feature logic will reside in the main repo, reducing indirection and simplifying debugging and development.
- Changes to pipeline code can be made directly in the main repo without requiring updates and releases of the lib repo.
- Testing and code quality standards will be preserved across both repositories.
