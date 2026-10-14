---
title: "Feature: _oci"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_oci/README.md
github_target_path: docs/reference/features/_oci.md
---

## Feature: _oci

### Description

Packages Garden Linux build artifacts (rootfs, kernel, initrd) into an [Open Container Initiative (OCI)](/reference/glossary#oci-oci-image-format)-compatible archive for upload to OCI registries.

### What it does

`_oci` invokes the `image` build script, which uses `onmetal-image` to bundle the raw rootfs, kernel (`vmlinuz`), and initrd into an OCI image stored in a local `onmetal/` directory. The result is compressed into a `.oci.tar.xz` archive.

The OCI image produced by this feature does not represent a runnable container. Instead, it encapsulates Garden Linux boot artifacts — rootfs, kernel, and initramfs — as OCI layers with custom media types (`vnd.onmetal.image.*`). This format is designed for infrastructure platforms (such as the onmetal project) that pull Garden Linux images from an OCI registry and boot them as virtual machines or bare-metal nodes.

After extracting the archive, you can tag and push the image using `onmetal-image`, inspect it via `onmetal-image inspect`, and resolve artifact URLs for individual layers such as the kernel.

> **Note:** Standard container runtimes (`docker`, `podman`) cannot pull or run these images because they do not contain a standard container filesystem layer.

For more information on working with the resulting artifact, see the [onmetal-image](https://github.com/onmetal/onmetal-image) project and the [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec/).

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`image`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_oci/image) ([`image`](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Build script that extracts kernel and initrd, runs `onmetal-image build` to assemble OCI layers, and produces the `.oci.tar.xz` archive. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_oci/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and the `.oci.tar.xz` artifact. |

### Related features

This feature has no include or exclude relationships.

### Further reading

- [onmetal-image project](https://github.com/onmetal/onmetal-image)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec/)

## Related topics

<RelatedTopics />

