## Feature: chost
### Description
<website-feature>
The `chost` feature adjusts Garden Linux to support running container and Kubernetes workload.
</website-feature>

### Features
The `chost` feature adjusts Garden Linux to support running container and Kubernetes workload and installs and configures all related packages like `containerd`.

### Unit testing
To be fully complaint these unit tests validate the extended capabilities on `ping` and `gstreamer`, the installed packages, correctly defined suids and sgids as well as the systemd unit files.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|server|
|excluded_features|None|
