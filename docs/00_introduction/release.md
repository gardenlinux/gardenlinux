# Garden Linux Releases

## Introduction

On this page you will learn about the Garden Linux releases and their lifecycle.

### Stable releases

You can expect up to four Garden Linux releases per year, published up to once per quarter. A new release _(e.g. 1443.0 or "release 1443")_ includes major changes like newer major version of software package or library. Within a release maintenance period, changes are published as release patches _(e.g. 1443.1 or "patch 1 of release 1443")_. Each release is maintained nine months, while going through following maintenance phases:

- **Standard maintenance** starts with the publishing of a new stable release and continues for six months. In this phase active maintenance is performed on the release. You can expect regular patches including _(but not limited to)_ fixes for issues, updates to higher minor release of selected software packages and libraries included, proactive monitoring & assessment of security vulnerabilities, performance corrections and enhancements and more. General best practice is to always use the latest patch of the latest release.

- **Extended maintenance** starts after the standard maintenance phase and continues for three months. In this phase only [Common Vulnerabilities and Exposures (CVE)](https://csrc.nist.gov/glossary/term/common_vulnerabilities_and_exposures) with high and critical (7.0-10.0) severity according to the [Common Vulnerability Scoring System (CVSS)](https://nvd.nist.gov/vuln-metrics) are patched. For more details refer to the [Garden Linux Security Response Process](/SECURITY.md). This enables users to have sufficient time to plan and execute their transition to latest release in standard maintenance.

- **End of maintenance** is reached nine months after the release has been published. In this phase no further planned maintenance activities are performed. Adopters can continue to use the release at their own risk. Users can request an exceptional patch via GitHub issue in [gardenlinux](https://github.com/gardenlinux/gardenlinux/issues/new/choose). There is no guarantee the request will be served - maintainers reserve the right to reject the request and fix-forward only in the latest release that is in standard maintenance due to the complexity involved with producing a patch for very old release.

### Nightly releases 

Triggered every night via the GitHub Action [Nightly Build](https://github.com/gardenlinux/gardenlinux/actions/workflows/nightly.yml). Their status can be monitored publicly in the action. The maintainers are striving towards having every 24 hours a successful build. This release contains latest software packages, aiming at rapid iterations for advanced stakeholders interested in the cutting-edge changes, but is not guaranteed to be always stable and as maintained/tested as the LTS releases. This release does not include maintenance commitments and therefore is not recommended for production scenarios. Up to once per quarter a daily release is promoted to stable release and accepted for nine months of standard maintenance.

## Schedule

### Active maintenance

In this section you can find more about the releases that are currently actively maintained and receive maintenance by the Garden Linux Maintainers team.

Garden Linux strives to balance providing cutting edge version of the relevant software packages and libraries, with enabling adopters to benefit from stable and sufficiently long maintenance phases reducing maintenance efforts. Therefore, a user can expect up to four releases every year, published maximum once per quarter. Each release goes through the phases listed in the [Introduction](#introduction) section.

**Current schedule:**

```mermaid
gantt
    title Garden Linux active LTS releases
    axisFormat %m.%y
    section '15xx*'
        Release:                milestone, 2024-07-22, 0m
        Standard maintenance:       task, 2024-07-22, 6M
        Extended maintenance:       milestone, 2025-01-22, 0m
        Extended maintenance:       task, 2025-01-22, 3M
        End of maintenance:         milestone, 2025-04-22, 0m
    section '1443'
        Release:                milestone, 2024-03-13, 0m
        Standard maintenance:       task, 2024-03-13, 6M
        Extended maintenance:       milestone, 2024-09-13, 0m
        Extended maintenance:       task, 2024-09-13, 3M
        End of maintenance:         milestone, 2024-12-13, 0m
    section '1312'
        Release:                milestone, 2023-11-03, 0m
        Standard maintenance:       task, 2023-11-03, 6M
        Extended maintenance:       milestone, 2024-05-03, 0m
        Extended maintenance:       task, 2024-05-03, 3M
        End of maintenance:         milestone, 2024-08-03, 0m
```

| Release                                                                   | Release date  | Extended maintenance  | End of maintenance    |
| -                                                                         | -             | -                     | -                     |
| next                                                                      | Dec 2024      | Jun 2025              | Sept 2025             |
| 15xx*                                                                     | 22.07.2024    | 22.01.2025            | 22.04.2025            |
| [1443](https://github.com/gardenlinux/gardenlinux/releases/tag/1443.0)    | 13.03.2024    | 13.09.2024            | 13.03.2024            |
| [1312](https://github.com/gardenlinux/gardenlinux/releases/tag/1312.0)    | 03.11.2023    | 03.05.2024            | 03.08.2024            |


\* Release in progress.

### Out of maintenance releases (archive)

In this section you can find more about the releases that are already out of maintenance and considered archived with no further maintenance expected. Only deviation could arise in an exceptional and extraordinary situation, which would require special agreement between the Garden Linux Maintainers and specific adopter. In general, if you are using a version listed below, you are encouraged to migrate as soon as possible to latest release in standard maintenance. 

| Release                                                                   | Release date  | Extended maintenance  | End of maintenance    |
| -                                                                         | -             | -                     | -                     |
| [934](https://github.com/gardenlinux/gardenlinux/releases/tag/934.0)      | 05.06.2023    | 05.12.2023            | 05.03.2024            |
| [576](https://github.com/gardenlinux/gardenlinux/releases/tag/576.0)      | 17.11.2021    | 17.05.2023            | 17.08.2023            |
| [318](https://github.com/gardenlinux/gardenlinux/releases/tag/318.4)      | 28.04.2021    | 28.10.2021            | 28.01.2023            |
| [184](https://github.com/gardenlinux/gardenlinux/releases/tag/184.0)      | 29.10.2020    | 29.04.2020            | 29.07.2021            |
| [27](https://github.com/gardenlinux/gardenlinux/releases/tag/27.0)        | 09.06.2020    | 09.12.2020            | 09.03.2021            | 


### Patches  

During the standard and extended maintenance periods the corrections are delivered via patch releases _("patches")_. They are considered stable, and adopters are encouraged to always use the latest patch of the latest stable release. Patch releases can be expected to adhere to following rules:

- Can include higher minor versions of software packages or libraries already included in the LTS release.
- Can include security enhancements related to vulnerabilities identified after the release of the previous patch.
- Can remove in rare (exceptional) situations software packages or libraries (e.g. due to security or legal risk identified after the release was published.). Such changes are documented in the release note. 

## Dictionary

To ensure common understanding of the terms involved, the terms used throughout the document are defined in this section.
- **Release** is used in the context of Garden Linux and referse to the process of publishing a new stable version of the Linux distribution.
- **Standard maintenance** is used in the context of Garden Linux releases, it refers to the initial six-month window after the release of new version of Garden Linux. 
- **Extended maintenance** is used in the context of Garden Linux releases, it refers to the three-month window after the end of standard maintenance.