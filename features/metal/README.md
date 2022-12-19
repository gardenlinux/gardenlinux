## Feature: metal
### Description
<website-feature>
This platform feature creates an artifact for (bare) metal systems.
</website-feature>

### Features
This feature creates a (bare) metal compatible image artifact as an `.iso` file and inlcudes further metal related stuff like standard kernel, grub, etc. that are required for physical components.


### Unit testing
This platform feature supports unit testing and is based on the `metal` fixture to validate the applied changes according its feature configuration.

### Meta
|||
|---|---|
|type|platform|
|artifact|`.raw`,`.qcow2`|
|included_features|`cloud`|
|excluded_features|None|
