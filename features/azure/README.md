## Feature: azure
### Description
<website-feature>
This platform feature creates an artifact for Microsoft Azure.
</website-feature>

### Features
This feature creates a Microsoft Azure compatible image artifact as a `.vhd` file.

To be platform compliant smaller adjustments like defining the platform related clocksource config, networking config etc. are done.
The artifact includes `cloud-init` for orchestrating the image.

### Unit testing
This platform feature supports unit testing and is based on the `azure` fixture to validate the applied changes according its feature configuration.

### Meta
|||
|---|---|
|type|platform|
|artifact|`.raw`, `.vhd`|
|included_features|cloud|
|excluded_features|None|
