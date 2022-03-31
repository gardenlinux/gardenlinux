## Garden Linux Repositories

Garden Linux is a Debian-based Operating System. Therefore it uses apt.

The location of sources are at `/etc/apt/sources.list` respectively in the folder `/etc/apt/sources.list.d/`

#### Default Repo:
	deb http://repo.gardenlinux.io/gardenlinux dev main

#### Generally:

	deb http://repo.gardenlinux.io/gardenlinux $GARDENLINUX_EPOCH main

`$GARDENLINUX_EPOCH` is generally `dev`, but the Garden Linux Version number can be defined here. It is the number of days since first Garden Linux release.

<details>
  <summary>More Info</summary>
  
Try running [bin/garden-version](bin/garden-version), to get the $GARDENLINUX_EPOCH value:
  ```
# ./bin/garden-version
    dev

# ./bin/garden-version --major
    730

# ./bin/garden-version --minor
    0
  ```
- --major prints the number of days after release and is the main version number of Garden Linux.
- --minor is mainly for security updates for older major versions.

The Source Line for this example should look like:

    deb http://repo.gardenlinux.io/gardenlinux 730.0 main
	

</details>

## Misc

- currently we keep old packages in `dev` dist, and I think we are keeping it that way for now.
- the repository contains own packages, and a selected set of packages mirrored from `debian testing`
- garden packages are being built in our gitlab pipelines


