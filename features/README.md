## Features
This is the Feature Folder. Each Folder describes one feature, which can be added at buildtime, e.g. ./build --features <feature1\>,<feature2\>

A Feature defines a set of packages and/or configurations. It can contain the following parts, which function is described shortly:

### currently available Platforms:
- metal (for Bare-Metal Systems)
- kvm (adapted metal, specialized for use in kvm-machines)
- ali (AliCloud)
- azure (Microsoft Azure)
- vmware (VMware Platform)
- 

#### info.yaml
This file contains basic information:
- a description/name of the feature,
- a type (either platform, element, flag), 
- other features, which are then included in this feature
- other elements (TODO)


#### exec.config
This file is used to add commands to run inside chroot of the current build, e.g. for configuration.
#### exec.pre
//Todo

seldomly used - more info coming soon
#### exec.post
//Todo


#### file.exclude
used to define unwanted files - after the build is done the outputimage won't contain files defined in this file
#### (dir) file.include
used to add files manually - 

the folder "file.include" represents "/" - e.g: 

if you want to add /etc/custom.file to Gardenlinux, just place that file "custom.file" inside file.include/etc/custom.file
#### pkg.exclude

define packages which are removed during build process, if they exist
#### pkg.include
~ package musthaves

define packages from official sources to install to the Gardenlinux Build
