---
title: "Feature: pythonDev"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/pythonDev/README.md
github_target_path: docs/reference/features/pythonDev.md
---

## Feature: pythonDev

### Description

Adds Python development tools (`pip`, `venv`, and `vim`) to the `python` base. For production images, consider a multistage container build instead.

### What it does

Installs `python3-pip`, `python3-venv`, and `vim`. Provides `exportLibs.py` for listing installed Python libraries. For production use, a multistage build with `bare-python` is recommended over including `pythonDev` in the final image.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/pythonDev/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Configures pip and venv defaults for the development environment. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/pythonDev/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/pythonDev/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/pythonDev/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `python3-pip`, `python3.14-venv`, `vim`. |
| [`file.include/usr/bin/exportLibs.py`](https://github.com/gardenlinux/gardenlinux/blob/main/features/pythonDev/file.include/usr/bin/exportLibs.py) ([`file.include`](/reference/features/#file-include)) | Utility script that exports a list of installed Python libraries to a file. |

### Related features

**Includes:**

- [`python`](/reference/features/python) — provides the Python 3 runtime required by development tools.

## Related topics

<RelatedTopics />

