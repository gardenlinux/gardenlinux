# Features

<website-features>

## General
Each folder represents a usable Garden Linux `feature` that can be added to a final Garden Linux artifact. This allows you to build Garden Linux for different cloud platforms with a different set of features like `CIS`, `read only` etc. Currently, the following feature types are available:

| Feature Type | Feature Name |
|---|---|
| Platform | ali, aws, azure, gcp, kvm, baremetal, ... |
| Feature | container host, virtual host, ... |
| Modifier | _slim, _readonly, _pxe, _iso, ... |
| Element | cis, fedramp, ... |

*Keep in mind that `not all features` may be combined together. However, features may in-/exclude other features or block the build process by given exclusive/incompatible feature combinations.*

## Selecting Features
 Desired features can be selected in the two ways.

 * Editing the [Makefile](../Makefile)
 * Explicit calling of `./build.sh --features <feature1\>,<feature2\>`

 ### Editing the [Makefile](../Makefile)
 The recommended way to change the features is by adjusting the [Makefile](../Makefile). This ensures the compability with our [documentation](../docs). Therefore, you may just change the block of your desired artifact.

 **Example:**

 If you want to add the `CIS` feature for `kvm-dev` you may adjust the [Makefile](../Makefile):

 From:
 ```
kvm-dev: container-build cert/sign.pub
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,kvm,_dev $(BUILDDIR) $(VERSION)
```
 To:
 ```
kvm-dev: container-build cert/sign.pub
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,kvm,cis,_dev $(BUILDDIR) $(VERSION)
```

Afterwards, the artifact can be created by executing `make kvm-dev`.


### Explicit Calling of `./build.sh --features <feature1\>,<feature2\>`
This method is slightly different from the first one and results in calling the `build.sh` directly, which is even called from the [Makefile](../Makefile). Within this method features can be directly given via the `cli`.

**Example:**

`./build.sh --features <feature1\>,<feature2\> [...]`


## File Structure
Following files may be placed inside a single feature folder. Except of the `info.yaml` all files are optional.

**Overview:**
| Filename | Description | Usage (Type) |
|---|---|---|
| info.yaml | Provides basic information for further orchestration | File (YAML) |
| pkg.exclude | Removes autoinstalled `.deb` packages | File (list): Package name per line |
| pkg.include | Installs `.deb` packages (must be present in repository) | File (list): Package name per line |
| exec.pre | Pre execution hook: Allows to run commands before `exec.config` is executed | File (Shell) |
| exec.config | Allows to run commands within the `chroot` during the build | File (Shell) |
| exec.post | Post execution hook: Allows to run commands after `exec.config` is executed | File (Shell) |
| file.include | Allows to add files to the artifact | Directory (with files): e.g. Rebuild the filesystem structure [file.include/etc/hosts] to overwrite the hostfile |
| file.exclude | Allows to remove files from the artifact | File (list): Absolute path to file to remove per line |

All files for features are described in detail below.

### info.yaml
`info.yaml` provides basic meta information for further orchestration.

**Filetype**: YAML
| Field  | Type | Description | Example |
|---|---|---|---|
| description | String | Short description of the feature | "The base layer for all other features. It pulls no extra packets only debootstap minbase" |
| type | String | Feature type | `element` |
| features | Dict | Includes lists of type `include`, `exclude` and `incompatible` | `incompatible` |
| (features) include | List (YAML) | List of features that should be included | `- cis` |
| (features) exclude | List (YAML) | List of features that should be excluded | `- cis` | 
| (features) incompatible | List (YAML) | List of features that are incompatible and can not run in combination with the parent feature | `- cis` |

**Example:**
*info.yaml:*
```
description: "The base layer for all other features. It pulls no extra packets only debootstap minbase"
type: element
features:
  include:
    - _slim
  exclude:
    - chost
  incompatible:
    - _readonly
```

Next to this, there may be some additional fields that are dedicated to their parent feature. These ones will be explained by their parent feature `README.md`.


### pkg.exclude
Removes autoinstalled `.deb` packages during the build process. These packages won't be included within the final artifact. These packages must be handled by local packet manager and already present. Not present packages will be ignored.

*This may also be helpful to remove unneeded or unwanted packages due to security/compatibility issues.*

**Usage:**

One package(name) per line.

**Example:**

*pkg.exclude:*
```
perl
screen
irssi
```


### pkg.include
Installs given packages from an included repository or by a given file path with minimal and needed dependency handling (recommended dependencies are ignored). Package(s) must be present within the used repositories or file system. Additional third-party repositories may be included (see [docs](../docs)). Packages will be installed before any further configuration starts. This may let you install packages and configure them afterwards.

**Usage:**

One package(name) per line.

**Example:**

*pkg.include:*
```
perl
screen
irssi
```


### exec.pre
Pre execution hook: Allows to run commands before `exec.config` is executed. This may be helpful to fulfill dependencies or to adjust task within the workflow.

**Usage:**

Shell/Bash/Python within the file

**Example:**

*exec.pre*
```
#!/usr/bin/env bash
set -Eeuo pipefail

useradd -m unittest
su - unittest
ssh-keygen -t rsa -C "for unittesting only"
```


### exec.config
Allows to run commands within the `chroot` during the chroot build process.

**Usage:**

Shell/Bash/Python within the file

**Example:**

*exec.config*
```
#!/usr/bin/env bash
set -Eeuo pipefail

/home/unittest/bin/unittest.sh
```


### exec.post
Post execution hook: Allows to run commands after `exec.config` is executed. This can be e.g. used to validate outputs or cleanup tasks.

**Usage:**

Shell/Bash/Python within the file

**Example:**

*exec.post*
```
#!/usr/bin/env bash
set -Eeuo pipefail

userdel unittest
rm -rf /home/unittest/
```


### file.exclude
Allows to remove files from the final artifact. Defined files will *not* be included within the image.

**Usage:**

One file(name) per line.

**Example:**

*file.exclude:*
```
/etc/motd
/etc/nginx/nginx.example.conf
```



### file.include
Allows to add files to the artifact. Within this special case, this represents a `directory` instead of a file. The filesystem structure is recreated within this directory and placed files will be included within the final artifact.

**Usage:**

Directory - recreated filesystem structure below this directory.

**Example:**

Example of a file structure that copies additional configurations for `nginx`.
```
file.include/
└── etc
    └── nginx
        ├── mime.conf
        ├── nginx.conf
        └── vhosts.d
            ├── bar.io.conf
            ├── foo.io.conf
            └── gardenlinux.io.conf
```
</website-features>
