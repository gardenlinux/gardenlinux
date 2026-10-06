## Feature: stackit

### Description

<website-feature>
This platform feature creates an artifact for STACKIT — a cloud platform by Schwarz Digits Cloud GmbH & Co. KG, built on OpenStack.
</website-feature>

### Features

This feature creates a STACKIT-compatible image artifact as a `.raw` file.

The image uses cloud-init with OpenStack/ConfigDrive as the primary datasource. Time synchronisation
is provided by chrony using the KVM PTP hardware clock (`/dev/ptp_kvm`) via the `ptp_kvm` kernel module,
which offers nanosecond-level precision by reading the host clock directly via hypercall — no NTP
server is required. The `ptp_kvm` module is loaded at boot via `modules-load.d` and a udev rule
creates the stable `/dev/ptp_kvm` symlink that chrony and systemd depend on.

### Meta

|||
|---|---|
|type|platform|
|artifact|`.raw`|
|included_features|`cloud`|
|excluded_features|None|
