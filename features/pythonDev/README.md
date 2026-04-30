---
title: "Feature: pythonDev"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/pythonDev/README.md
github_target_path: docs/reference/features/pythonDev.md
---

## Feature: pythonDev
### Description
<website-feature>
The `pythonDev` feature adds additional dev tools like pip or venv to enable python development.
</website-feature>

### Features
- pip: Install python packages
- venv: develop in virtual environments

### Production
For production, we recommend using a [multistage build with bare-python](https://github.com/gardenlinux/gardenlinux/blob/main/docs/01_developers/bare_container.md#adding-dependencies).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|python|
|excluded_features|None|
