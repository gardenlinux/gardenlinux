## Feature: vagrant
### Description
<website-feature>
This feature flag adds vagrant libvirt to the Garden Linux artifact.
</website-feature>

## Setup

Only tested on linux hosts so far.

Based on [this StackExchange answer](https://unix.stackexchange.com/questions/222427/how-to-create-custom-vagrant-box-from-libvirt-kvm-instance/222907#222907).

Ensure [vagrant](https://developer.hashicorp.com/vagrant/downloads?product_intent=vagrant), [libvirt](https://libvirt.org) and [the libvirt provider for vagrant](https://github.com/vagrant-libvirt/vagrant-libvirt) are set up.

Download the built artifact with a name like `gardenlinux_libvirt*.box`, where the cpu architecture matches yours.

Run the following commands to create and start a vagrant vm with Garden Linux:

```
vagrant box add --name gardenlinux gardenlinux_libvirt.box
vagrant init gardenlinux
vagrant up --provider=libvirt
```

### Features
**Warning**: Never use this feature on production!

### Unit testing
This feature does not support unit tests.

### Meta
|||
|---|---|
|type|flag|
|artifact|None|
|included_features|None|
|excluded_features|None|
