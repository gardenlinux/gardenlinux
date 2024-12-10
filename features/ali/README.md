## Feature: ali
### Description
<website-feature>
This platform feature creates an artifact for Alibaba cloud (Aliyun).
</website-feature>

### Features
This feature creates an Alibaba cloud compatible image artifact as an `.qcow2` file.

To be platform compliant smaller adjustments like defining the platform related ntp systems, networking config etc. are done.
The artifact includes `cloud-init` for orchestrating the image.

### Unit testing
This platform feature supports unit testing and is based on the `ali` fixture to validate the applied changes according its feature configuration.

### Meta
|||
|---|---|
|type|platform|
|artifact|`.raw`,`.qcow2`|
|included_features|cloud|
|excluded_features|None|
