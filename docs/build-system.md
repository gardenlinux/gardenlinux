# Garden Linux Build System


## Makefile
The [../Makefile](../Makefile) is the main entry point for the build system.

For each release target a makefile target exists, which calls `build.sh` with a pre-defined set of features.
For local builds for development purposes, the `Makefile` also prepares the secure boot keys.


## build.sh

Given a set of input parameters, the [../build.sh](../build.sh) script orchestrates the [build](#garden-build) and [test](garden-test).
Both, build and test, are executed in a container. The build container is also prepared by [../build.sh](../build.sh).

## garden-build


The [../bin/garden-build](../bin/garden-build) artifacts based on a given set of features. 

The following steps are executed per feature

| # | Step            | required feature file | Handled by                            | Description                                 |
|---|-----------------|-----------------------|---------------------------------------|---------------------------------------------|
| 1 | Package Include | pkg.include           | [garden-init](../bin/garden-init)     | Install packages required by the feature    |
| 2 | Package Exclude | pkg.exclude           | [garden-init](../bin/garden-init)     | Removes packages to comply with the feature |
| 3 | Configuration   | exec.config, exec.pre | [garden-config](../bin/garden-config) | Configuration required by the feature       |
| 4 | File Include    | file.include          | [garden-config](../bin/garden-config) | Include files required by the feature       |
| 5 | File Exclude    | file.exclude          | [garden-config](../bin/garden-config) | Remove files to comply with feature         |

The feature system is documented [here](../features/README.md) 


## garden-test

The [../bin/garden-test](../bin/garden-test) starts unit for a given image.
Unit tests are defined per feature. 


## Local Build Artifacts

Build artifacts are stored in the output folder (default `.build/`).
Some artifacts will only be created by certain features.



