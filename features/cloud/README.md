## Feature: cloud
### Description
<website-feature>
This feature adjusts Garden Linux for cloud functionality with cloud kernel, boot optimizations, etc.
</website-feature>

### Features
All hyperscaler & cloud platforms (e.g. `ali`, `azure`, `vmware`, `openstack`, etc.) are based on this `cloud` feature. Garden Linux artifacts with cloud functionality are highly optimized for cloud/hyperscaler environments by running on ARM64 or AMD64 hardware platforms including optimized kernel and boot options.

### Unit testing
this feature supports unit tests and ensures that all required packages are present, an autologout is configured, PAM faillock is active and the wireguard kernel module is activated.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|server|
|excluded_features|None|
