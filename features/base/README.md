## Feature: base
### Description
<website-feature>

This feature installs the `base` layer for Garden Linux.
</website-feature>

### Features
All artifacts/images are based on the `base` layer which represents a minimal setup to run the OS itself. This gets achieved by debootstrapping the `minbase` variant.
Within this feature all OS related base configurations (which still might get adjusted by other features on top of it) are performed.

### Unit testing
Representing the base layer for Garden Linux requires many additional unit tests. Unit tests will ensure that kernel options are correctly defined, debsums matches, no duplicated uids or gids are present, password hash policies are defined and many more. Additional checks like `rkhunter` are also performed. Not all unit tests may work on all fixtures since they may require a running system (e.g. for validating the kernel options).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|`_slim`|
|excluded_features|None|
