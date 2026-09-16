## Feature: stackit

### Description

<website-feature>
This platform feature creates an artifact for STACKiT — SAP's cloud platform built on OpenStack.
</website-feature>

### Features

This feature creates a STACKiT-compatible image artifact as a `.raw` file.

The image uses cloud-init with OpenStack/ConfigDrive as the primary datasource. Time synchronisation
is provided by chrony using the KVM PTP hardware clock (`/dev/ptp0`) via the `ptp_kvm` kernel module,
which offers nanosecond-level precision by reading the host clock directly via hypercall — no NTP
server is required.

### Meta

|||
|---|---|
|type|platform|
|artifact|`.raw`|
|included_features|`cloud`|
|excluded_features|None|
