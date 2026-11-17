---
title: "Feature: _fips"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_fips/README.md
github_target_path: docs/reference/features/_fips.md
---

## Feature: _fips

### Description

Enables [Federal Information Processing Standard (FIPS)](/reference/glossary#federal-information-processing-standard-fips) 140-3 mode for cryptographic operations in Garden Linux.

### What it does

`_fips` configures the system to operate in [FIPS 140-3](https://csrc.nist.gov/pubs/fips/140-3/final) compliance mode. It installs the required FIPS-validated cryptographic providers (`openssl-provider-fips`, `libgnutls28-dev`, `libssl-dev`, `gnutls-bin`) and places configuration files that activate the OpenSSL FIPS provider, enable FIPS mode for `libgcrypt`, and add `fips=1` to the kernel command line. A dracut configuration ensures the FIPS modules are included in the initrd.

The `exec.config` and `exec.late` scripts adjust runtime configuration, and the `file.include.markers.yaml` maps coverage markers to tests that verify FIPS is correctly activated.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fips/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Configures the image at build time to activate FIPS providers and finalize the FIPS setup. |
| [`exec.late`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fips/exec.late) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies final FIPS-related changes after all packages are installed. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fips/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs for FIPS verification tests. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fips/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fips/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs FIPS-validated cryptographic libraries and tools, including `openssl-provider-fips` and `gnutls-bin`. |
| [`file.include/etc/system-fips`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fips/file.include/etc/system-fips) ([`file.include`](/reference/features/#file-include)) | Marker file that signals to system components that FIPS mode is active. |
| [`file.include/etc/dracut.conf.d/10-fips.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fips/file.include/etc/dracut.conf.d/10-fips.conf) ([`file.include`](/reference/features/#file-include)) | Instructs dracut to include the `fips` module so FIPS mode is initialized before the root filesystem mounts. |
| [`file.include/etc/gcrypt/fips_enabled`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fips/file.include/etc/gcrypt/fips_enabled) ([`file.include`](/reference/features/#file-include)) | Enables FIPS mode for `libgcrypt`-based applications. |
| [`file.include/etc/kernel/cmdline.d/30-fips.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fips/file.include/etc/kernel/cmdline.d/30-fips.cfg) ([`file.include`](/reference/features/#file-include)) | Adds `fips=1` to the kernel command line to enforce FIPS mode at boot. |
| [`file.include/etc/update-motd.d/06-logo`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_fips/file.include/etc/update-motd.d/06-logo) ([`file.include`](/reference/features/#file-include)) | Adds a FIPS-mode indicator to the message of the day displayed at login. |

### Related features

This feature has no include or exclude relationships.

### Further reading

- [FIPS 140-3](https://csrc.nist.gov/pubs/fips/140-3/final)

## Related topics

<RelatedTopics />

