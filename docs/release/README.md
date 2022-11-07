# Release TOC
- [Release TOC](#release-toc)
- [General](#general)
  - [Versioning](#versioning)
  - [Naming in GIT](#naming-in-git)
    - [Beta](#beta)
    - [Stable](#stable)
- [Release Process](#release-process)
  - [Planning](#planning)
  - [Implementation](#implementation)
  - [Packaging](#packaging)
  - [Freeze](#freeze)
    - [Github](#github)
    - [Gitlab](#gitlab)
      - [Major releases](#major-releases)
      - [Minor & patch releases](#minor--patch-releases)
  - [Tagging](#tagging)
  - [CI/CD](#cicd)

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
During the freeze time the rules for making changes to the source code or any other related components become more strict and should highly be avoided. This means that usually no further features will be integrated, package versions upgraded etc. These enhancements and features will be hold back for the next upcoming release development. Changes during the freeze time may mostly affect (urgent) bugfixes or security related issues. This especially effects the major development platforms for Garden Linux like Github and Gitlab.

### Github
While Github represents Garden Linux' main source code platform a successful [nightly build](https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml) is mandatory for proceeding with the release. Therefore, all major platforms are covered by the nightly build pipeline which may indicate the stability for each of them.

Next to this, no further new features are added to `main` to not affect the stability of the builds, as well as of changing the defined release scope.


### Gitlab
Gitlab is mainly used for `.deb` based packages in each way. This means, that within Gitlab all (re)packaging and mirroring is done. This also includes the whole kernel and driver building and packaging. More and detailed information for the release pipeline can be found [here](https://gitlab.com/gardenlinux/gardenlinux-package-build/-/tree/main/packages).

#### Major releases
Therefore, major releases and their corresponding packages are created automatically based on their package manifest. This manifest is called [today.yaml](https://gitlab.com/gardenlinux/gardenlinux-package-build/-/blob/main/packages/today.yaml) and creates the latest `today` release.


#### Minor & patch releases
Minor & patch releases are semi automated. However, it just needs an additional release specific release manifest as a `.yaml` file in `gardenlinux-package-build/packages` (see also https://gitlab.com/gardenlinux/gardenlinux-package-build/-/tree/main/packages). The package definitions look slightly different to the regular `today.yaml`. Package versions and referenced mirrors must be pinned according to the recent base release.

**Creating the release manifest:**

Given by the example of the release [934.1](https://gitlab.com/gardenlinux/gardenlinux-package-build/-/blob/main/packages/934.1.yaml) a new `934.1.yaml` was placed within the `gardenlinux-package-build/packages` directory. The [release pipeline](https://gitlab.com/gardenlinux/gardenlinux-package-build/-/blob/main/driver/run#L58-59) automatically proceeds all present `.yaml` files daily.

**Pinning package versions and mirrors:**

Package versions and used mirrors must be pinned to the specific day that the patch release is based on. Without further pinning the pipeline would always use `latest` which would result in a new major release instead.

Example [943.1.yaml](https://gitlab.com/gardenlinux/gardenlinux-package-build/-/blob/main/packages/934.1.yaml):

```
---
version: "934.1"

publish:
  sources:
  - type: exclude
    packages:
    - matchBinaries:
      - apt-utils
    - matchSources:
      - db5.3

  - type: repo
    name: gardenlinux
    packages:
    - matchSources:
      - cyrus-sasl2/2.1.28+dfsg-8gardenlinux1
      - dracut/057-1gardenlinux1
      - frr/8.3.1-0gardenlinux1
      - gardenlinux-selinux-module/1.0.8
      - iproute2/5.19.0-1gardenlinux1
      - linux-5.15/5.15.77-0gardenlinux1
      - linux-signed-5.15-amd64/5.15.77+0gardenlinux1
      - linux-signed-5.15-arm64/5.15.77+0gardenlinux1
      - metalbond/0.2.0-0gardenlinux3
      - microsoft-authentication-library-for-python/1.20.0-1gardenlinux1
      - onmetal-image/0.0~git20220927.d73b45a-1gardenlinux1
      - pam/1.5.2-2gardenlinux1
      - perl/5.34.0-5gardenlinux1
      - python3.10/3.10.7-1gardenlinux1
      - refpolicy/2:2.20220520-2gardenlinux1
      - selinux-basics/0.5.8garden1
      - sops/3.7.3-0gardenlinux1
      - systemd/251.5-2gardenlinux1

  # Use bookworm from the 934.0
  # release as a base
  - type: mirror
    name: debian:bookworm:934

  # Mirror Debian sid from 946.0
  # since it contains the new OpenSSL
  # version 3.0.7
  - type: mirror
    name: debian:sid:946
    packages:
    - matchSources:
      - openssl
```
<br>

**Release versioning:**

The release definition is done by the key `version` and represents the release manifest's filename:

```version: "934.1"```

The underlying base release `934.0` is defined within the following section:
```
  # Use bookworm from the 934.0
  # release as a base
  - type: mirror
    name: debian:bookworm:934
```
*Note: It is not necessary to explicitly define a `.0` release. Therefore, you may just write `debian:bookworm:934`.* <br><br>

**Version pinning:**

Afterwards, the the pinned versions and mirrors may be defined. First, we start with the pinned versions from the Garden Linux repository. This structure is equal to the regular one just by adding the pinned version string to each package:
```
  - type: repo
    name: gardenlinux
    packages:
    - matchSources:
      - cyrus-sasl2/2.1.28+dfsg-8gardenlinux1
      - dracut/057-1gardenlinux1
      - frr/8.3.1-0gardenlinux1
      - gardenlinux-selinux-module/1.0.8
      - iproute2/5.19.0-1gardenlinux1
      - linux-5.15/5.15.77-0gardenlinux1
      - linux-signed-5.15-amd64/5.15.77+0gardenlinux1
      - linux-signed-5.15-arm64/5.15.77+0gardenlinux1
      - metalbond/0.2.0-0gardenlinux3
      - microsoft-authentication-library-for-python/1.20.0-1gardenlinux1
      - onmetal-image/0.0~git20220927.d73b45a-1gardenlinux1
      - pam/1.5.2-2gardenlinux1
      - perl/5.34.0-5gardenlinux1
      - python3.10/3.10.7-1gardenlinux1
      - refpolicy/2:2.20220520-2gardenlinux1
      - selinux-basics/0.5.8garden1
      - sops/3.7.3-0gardenlinux1
      - systemd/251.5-2gardenlinux1
```
<br>

**Mirror pinning:**

Within this example, also an external mirror is used for `openssl` and obtained from `debian:sid:946` which includes a newer package version. The only change to the regular behaviour is switching the `type` to `mirror` (instead `repo` for using the Garden Linux repository) and the mirror's name to the desired one:
```

  # Mirror Debian sid from 946.0
  # since it contains the new OpenSSL
  # version 3.0.7
  - type: mirror
    name: debian:sid:946
    packages:
    - matchSources:
      - openssl
```

## Tagging

## CI/CD
