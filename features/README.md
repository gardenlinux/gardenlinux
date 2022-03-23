## Features
This is the Feature Folder. Each Folder describes one feature, which can be added at buildtime, e.g. 

	./build --features <feature1\>,<feature2\>

A Feature defines a set of packages and/or configurations. It can contain the following parts, which function is described shortly:

| Feature Type | Includes |
|---|---|
| Platforms | ali, aws, azure, gcp, kvm, baremetal... |
| Features | container host, virtual host, ... |
| Modifiers | _slim, _readonly, _pxe, _iso ... |
| Element | cis, fedramp |

___

## File Structure

These Files can be placed inside a Feature Folder. Besides the info.yaml, all of them are optional.

#### info.yaml
This file contains basic information:
- a description/name of the feature,
- a type (either platform, element, flag), 
- other features, which are then included in this feature
- other elements (TODO)


___

#### pkg.exclude

define packages which are removed during build process, if they exist (e.g. because of security/compatibility issues)

#### pkg.include
~ package musthaves

define packages from official sources to install to the Gardenlinux Build

pkg.include is triggered as the first step before any configuration

Only necessary files are installed - recommended files are ignored

#### exec.config

This file is used to add commands to run inside chroot of the current build, e.g. for configuration.

#### exec.pre
TODO

seldomly/never used currently

These commands are ran inside the docker build environment

#### exec.post
TODO


#### file.exclude
used to define unwanted files - after the build is done the outputimage won't contain files defined in this file
#### (dir) file.include
used to add files manually - 

the folder "file.include" represents "/" - e.g: 

if you want to add /etc/custom.file to Gardenlinux, just place the file "custom.file" at file.include/etc/custom.file
