## Feature: openstack
### Description
<website-feature>
This platform feature creates an artifact for OpenStack (CCEE) systems.
</website-feature>

### Features
This feature creates an OpenStack (CCEE) ompatible image artifact as a `.raw`, `.qcow2` and `.vmdk` file.
This particular feature set for Garden Linux on OpenStack is for an OpenStack landscape that uses VMware ESXi as hypervisor (which is why you will find `open-vm-tools` in `pkg.include`). If you want to run Garden Linux on OpenStack, you will most likely have to create your own feature set that matches your environment and hypervisor.
A word of **WARNING**: Since OpenStack is an open environment, we can only provide a reference implementation at this point.

### Unit testing
This platform feature supports unit testing and is based on the `openstackccee` fixture to validate the applied changes according its feature configuration.

### Meta
|||
|---|---|
|type|platform|
|artifact|`.raw`,`.qcow2`, `.vmdk`|
|included_features|cloud|
|excluded_features|None|
