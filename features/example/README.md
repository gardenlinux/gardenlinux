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
| image | Provides the possibility for creating an additional output artifact | File (Shell) |
| convert | Provides the possibility to convert a given artifact to another artifact type | File (Shell) |
| file.include | Allows to add files to the artifact | Directory (with files): e.g. Rebuild the filesystem structure [file.include/etc/hosts] to overwrite the hostfile |
| file.include.stat | Allows to edit permissions and owner of files | Per line to define: `$userOwner $groupOwner $filePermission $fileName` |
| file.exclude | Allows to remove files from the artifact | File (list): Absolute path to file to remove per line |
| test | Providing feature related unit tests that can be performed on different target platforms by Pytest fixtures | Directory: Contains `PyTest` based unit tests (must be prefixed with `test_` and suffixed by `.py`) |

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


### README.md

Besides giving information, this file is also used as information source for the Garden Linux Website: As Unification we decided to add a paragraph after the main title, which is masked by \<website-feature> \</website-feature>, so an extraction script is able to find the relevant content.

Have a look at the Raw Code (!) for `README.md` inside [features/example](../features/example) for a detailed example.


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
Installs given packages from the Garden Linux repository or by a given file path or file uri with minimal and needed dependency handling (recommended dependencies are ignored). Packages will be installed before any further configuration starts. This may let you install packages and configure them afterwards.

*Hint: During the feature development the native Debian repository can additionally be used by adding `--debian-mirror` to the `build.sh`. Please take note that this is not supported for production builds and will raise an error. Therefore, needed packages must be repackaged or be mirrored on the Garden Linux repository.*

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


### image
image hook: Allows to run shell commands which can be used to create additional output artifact. This can be used if multiple output files are needed.

**Usage:**

Shell/Bash/Python within the file

**Example:**

*image*
```
#!/bin/bash

set -Eexuo pipefail

rootfs="$1"
targetBase="$2"

rootfs_work="$(mktemp -d)"
cp -a "$rootfs/." "$rootfs_work"

find "$rootfs_work/var/log/" -type f -delete

chcon -R system_u:object_r:unlabeled_t:s0 "$rootfs_work"
#chroot "$rootfs_work" /usr/bin/env -i /sbin/setfiles /etc/selinux/default/contexts/files/file_contexts /
rm "$rootfs_work/.autorelabel"

file="$(mktemp)"

size="${size:-$(du -sb "$rootfs_work" | awk '{ min_size_bytes = min_size * MB; size = $1 * 1.5; padded_size = size + (MB - (size % MB) % MB); if (padded_size < min_size_bytes) padded_size = min_size_bytes; print (padded_size / MB) "MiB" }' "MB=1048576" "min_size=64")}"
truncate -s "$size" "$file"

timestamp=$(garden-version --epoch "$version")
make_reproducible_ext4 -t "$timestamp" -h "gardenlinux:$version:firecracker:rootfs" -m -p 16 "$rootfs_work" "$file"

rm -rf "$rootfs_work"

cp "$rootfs/boot/vmlinu"*"-firecracker-${arch}" "$targetBase.vmlinux"
cp "$file" "$targetBase.ext4"

rm "$file"
```


### convert
convert hook: Allows to run shell commands which can be used to convert an already present artifact into another output format.

**Usage:**

Shell/Bash/Python within the file

**Example:**

*exec.post*
```
#!/usr/bin/env bash
set -Eeuo pipefail

dir="$(dirname "$(readlink -f "$BASH_SOURCE")")"

qemu-img convert -o subformat=streamOptimized -o adapter_type=lsilogic -f raw -O vmdk "$1.raw" "$1.vmdk"
make-ova --vmdk "$1.vmdk" --guest-id debian10_64Guest --template "$REPO_ROOT/features/vmware/vmware.ovf.template"
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


### file.include.stat
Allows to change user, group and file permissions to files within the Garden Linux image. Each line represents a change for a single file.

**Usage:**
For each line all values need to be defined:
```$userOwner $groupOwner $filePermission $fileName```

**Example:**

```
# <user> <group> <mode> <filename>
irc irc 777 /etc/test
nginx nginx 0640 /etc/nginx/conf.d/vhosts/01-www.gardenlinux.io.conf
```



### test
Allows to add additional and feature related (unit) tests. All tests are based on `PyTest` and can be performed on all or on only desired target platforms or hyperscaler if desired. Target platforms can be in-/excluded by `fixtures`. More information about tests and how to run them can be found [here](../tests/README.md).


**Usage:**

Directory: Place unit test files.
Prefix: `test_`
Suffix: `.py`
Example name: `test_example_consistency.py`

**Example:**
```
test
├── debsums.disable
├── test_autologout.py
├── test_packages_musthave.py
├── test_pam.py
├── test_pam_faillock.py
└── test_wireguard.py
```

</website-features>
