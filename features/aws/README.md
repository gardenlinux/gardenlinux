## Feature: aws
### Description
<website-feature>
This platform feature creates an artifact for Amazon AWS.
</website-feature>

### Features
This feature creates an Amazon AWS compatible image artifact as an `.raw` file.

To be platform compliant smaller adjustments like defining the platform related clocksource config, networking config etc. are done.
The artifact includes `cloud-init` and `amazon-ec2-utils` for orchestrating the image.

### Unit testing
This platform feature supports unit testing and is based on the `aws` fixture to validate the applied changes according its feature configuration.

### Meta
|||
|---|---|
|type|platform|
|artifact|`.raw`|
|included_features|cloud|
|excluded_features|None|
