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
      - [Minor \& patch releases](#minor--patch-releases)
  - [Tagging](#tagging)
    - [Github](#github-1)
    - [Gitlab](#gitlab-1)
  - [CI/CD](#cicd)
    - [Artifact creation](#artifact-creation)
    - [Artifact testing](#artifact-testing)

# General
Garden Linux frequently publishes snapshot releases. Beside this, beta and stables releases are published. Releases are available as machine images for most major cloud providers as well as file-system images for manual import. Release artifacts can be found within the [Github release section](https://github.com/gardenlinux/gardenlinux/releases).

## Versioning
The version number is calculated by [bin/garden-version](https://github.com/gardenlinux/gardenlinux/blob/main/bin/garden-version) which uses the [VERSION](https://github.com/gardenlinux/gardenlinux/blob/main/VERSION) file.
For release branches, the VERSION file contains the Garden Linux version to build. The main branch`VERSION` file contains `today`, which tells the `bin/garden-version` to calculate the version of today.

## Branches
Each day a version of Garden Linux is build from the main branch via the [nightly](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/nightly.yml) GitHub action. 
Release branches start with `rel-` and are used to publish Garden Linux images to supported Cloud Providers.  


Branches are also used for development, the branch naming convention is described [here](https://github.com/gardenlinux/gardenlinux/blob/main/CONTRIBUTING.md#git-branch-naming-convention)).

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
### Github
After having all features completed and included within the `main` branch on Github, a corresponding git tag may be set. This git tag represents the status of the git branch during the development at the time where it has been set. All current tags and releases can be found [here](https://github.com/gardenlinux/gardenlinux/tags).


 The tag will be set as:
```
# Format
$major.$minor

# Example:
943.1
```

A tag can be set by:
```
git tag $major.$minor
git push --tags
```

### Gitlab
Repository packages are maintained and built within the Gitlab pipeline. Garden Linux packages which are built by this pipeline are either versioned based on the source package provided by the configured distribution (e.g. debian:bookworm) or the version provided by the corresponding Git tag of the package project. In both cases, the Debian version of the package defines the general Garden Linux package version. It is then extended by a Garden Linux specific suffix in order to distinguish Garden Linux packages from their original Debian packages.

If a commit is related to a Git tag however, the Git tag defines the whole package version. Thus, it must have the following structure to fit the general version schema:

```
gardenlinux/<Debian version>gardenlinux<count>
gardenlinux/2.1.27+dfsg2-3gardenlinux1
```

Here, the count must be increased each time a Git tag already exists for the given Debian version. This allows us to release multiple Garden Linux packages for the same Debian version. Since, the tag defines how the Garden Linux package version will look like, it must be unique.

Defining a git tag on a package will automatically include the package as the release version for an overall Garden Linux release. See also further [docs](https://gitlab.com/gardenlinux/gardenlinux-package-build).

## CI/CD
### Artifact creation
Releases are automatically created - for example a [nightly job](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/nightly.yml) release will created on a daily base at 6 AM. These releases are created by Github workflows and can be found in the subdirectory `.github`. These jobs are orchestrated by the [build config](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/build.yml). According to the [build config](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/build.yml) artifacts for `amd64` and `arm64` will be created for [all major platforms](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/build.yml#L53-L54).

The same applies for the [release job](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/release.yml) that creates the final production artifacts with `gardener` support. Afterwards, the [release.sh script](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/release.sh) will upload the final artifacts to Github via the Github API.

### Artifact testing
Created images will be tested - this includes further unit- & platform integration tests. These tests are orchestrated by the [tests.yml config](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/tests.yml). Tests will run on all major platforms and are based on Pytest. The whole Pytest documentation for unit, platform and integration tests can be found [here](https://github.com/gardenlinux/gardenlinux/tree/main/tests).