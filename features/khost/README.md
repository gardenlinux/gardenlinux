## Feature: khost
### Description
<website-feature>
The vhost feature adjusts Garden Linux to support running Kubernetes (vanilla) workloads.
</website-feature>

### Features
The `khost` feature adjusts Garden Linux to support running Kubernetes (vanilla) workloads and installs and configures all related packages (regarding the used hardware architecture) and tools. It adjusts the `kublets`, `sysctl` and removes any swap partition.

### Unit testing
Unit tests will ensure that the needed packages are present as well as the `kublet` is enabled within `systemd`.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|`chost`|
|excluded_features|None|
