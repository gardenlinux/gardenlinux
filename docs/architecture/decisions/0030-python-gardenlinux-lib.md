# 30. Defining python-gardenlinux-lib as an internal tool

Date: 2026-01-21

## Status

Accepted

## Context

The original reason to introduce the `python-gardenlinux-lib` was to clean up other repositories from single-purpose python scripts to improve reusability, allow unit testing and enhance code quality.

Therefore, pipeline and `/hack` scripts from the main repository have been refactored and moved to the `python-gardenlinux-lib`. In order to make the usage in pipelines still feasible, a GitHub Action to install the library is provided.

However, as the `python-gardenlinux-lib` grows more and more, some scripts caused discussions about whether they fit into the scope of the `python-gardenlinux-lib` or not.

To provide a basis for these discussions, this ADR defines the scope of the `python-gardenlinux-lib`, which should be taken into account, as long as there is no other ADR deprecating this one.

## Decision

- The `python-gardenlinux-lib` is an internal tool for the development and operations of Garden Linux, **not** a product
- Python scripts in this scope **should** be included in `python-gardenlinux-lib`, but do **not have to**, if a valid reason is provided
- Python scripts used for pipelines, usually stored at `gardenlinux/.github/workflows`, **must always** be moved to the `python-gardenlinux-lib`
- If the target group includes the users of Garden Linux, even if developers are the main target, the python script **must not** be included in `python-gardenlinux-lib`

## Consequences

- The only intended group using `python-gardenlinux-lib` are Garden Linux developers
- The `python-gardenlinux-lib` is not required to have an official release schedule or official support
- Scripts targeted to users may contain duplicated code and have to be tested separately 
- Pipeline scripts are stored indirectly
    - Therefore, if no version was specified, it will always use the latest script version and not the script version of the potentially older branch
