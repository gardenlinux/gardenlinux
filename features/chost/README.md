## Feature: chost
### Description
<website-feature>
The `chost` feature adjusts Garden Linux to support running container and Kubernetes workload.
</website-feature>

### Features
The `chost` feature adjusts Garden Linux to support running container and Kubernetes workload and installs and configures all related packages like `containerd`.

### Unit testing
To be fully compliant these unit tests validate the installed packages, correctly defined suids and sgids as well as the systemd unit files.

TODO
cosign
nerdctl
bypass4netns
buildkit

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|server|
|excluded_features|None|
