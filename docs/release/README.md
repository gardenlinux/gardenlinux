# Release TOC
- [Release TOC](#release-toc)
- [General](#general)
  - [Versioning](#versioning)
  - [Naming in GIT](#naming-in-git)
    - [Beta](#beta)
    - [Stable](#stable)
- [Release Process](#release-process)
  - [first](#first)
  - [second](#second)
  - [third](#third)

# General
Garden Linux frequently publishes snapshot releases. Beside this, beta and stables releases are published. Releases are available as machine images for most major cloud providers as well as file-system images for manual import. Release artifacts can be found within the [Github release section](https://github.com/gardenlinux/gardenlinux/releases).

## Versioning
Versioning is done by the [garden-version](https://github.com/gardenlinux/gardenlinux/blob/main/bin/garden-version) script. In default, it returns just `today` by working on a regular git branch with its [versionfile](https://github.com/gardenlinux/gardenlinux/blob/main/VERSION) (also often called `$versionfile`).

If no parameter is specified the full version &#60;major&#62;.&#60;minor&#62; e.g. 27.5 is printed. The version is taken from the `versionfile`. On HEAD this should always evaluate to 'today', on branch versions this always should resolve to the next version that will be build e.g. 27.1. This implies there is no branch with a .0 in the `versionfile` file.
The version calculated expresses the days since $startdate and is always UTC based.

## Naming in GIT
Garden Linux's source code is maintained and versioned in a git project on GitHub. While mostly branches are being used for feature implementations, docs and further enhancements (see also [branch naming convention](https://github.com/gardenlinux/gardenlinux/blob/main/CONTRIBUTING.md#git-branch-naming-convention)) releases are based on git tags where we distinguish between beta and stable releases. An overview of all tags (releases) can be found [here](https://github.com/gardenlinux/gardenlinux/tags).

### Beta
Beta releases are tagged by a `beta_` prefix as well as their version.
|   |   |
|---|---|
| Syntax | beta_&#60;major&#62;.&#60;minor&#62; |
| Example | beta_940.0 |


### Stable
Stable releases are just tagged by their version.
|   |   |
|---|---|
| Syntax | &#60;major&#62;.&#60;minor&#62; |
| Example | 576.12 |

# Release Process
## first
## second
## third