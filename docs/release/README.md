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
## Planning
* Decide what features should be part of the next release
* Create corresponding issues.
* Label those issues with the `version/next` label.
## Implementation
* Reference style guides and the contribution documentation.
* Make sure users know how branch should be named.
* Describe how features are implemented and later reviewed.
## Packaging
* Briefly describe how the packaging process works
  * The `today` and the major version of each day (e.g. 946.0) is created automatically each day
  * There is no special task needed for the first major release of a day.
  * Only if a patch release is created (e.g x.1, x.2, x.3, ...), then a manual task is needed.
* Upgrade the Linux Kernel to the latest patchlevel. 
  * Releasing a new kernel is documented in the [GL kernel repo](https://gitlab.com/gardenlinux/gardenlinux-package-linux-5.15).
* Reference the following documentation:
  * https://gitlab.com/gardenlinux/gardenlinux-package-build/-/blob/main/README.md
  * https://gitlab.com/gardenlinux/gardenlinux-package-build/-/blob/main/docs/repo.md
  * https://gitlab.com/gardenlinux/gardenlinux-package-build/-/blob/main/packages/README.md
* Modification to the `today.yaml` define how the packages will look like in the Garden Linux repo once a new release would be created
## Freeze
### Github
* Ensure that no new features are added to main
* Make the main branch stable
  * In order to have a release, a successful nightly build is crucial since those are the base for the release artifacts
### Gitlab
* Major releases and their packages are created automatically based on the today.yaml
* If it's a patch release, a corresponding package definition for the patch must be created manually
  * The package definition looks slightly different to the `today.yaml`
    * There is no need to define the mirrors once again. Only the publishing configuration is important.
    * Versions of the Garden Linux packages must be pinned because the package definitions are evaluated each day 
      and without version pinning, the patch release would always get the newest Garden Linux packages available
    * The same applies to the referenced mirrors. They should be pinned to the specific day that the patch release is based on.
## Tagging

## CI/CD
