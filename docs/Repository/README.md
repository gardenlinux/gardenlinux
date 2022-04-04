## Garden Linux Repositories

Garden Linux is a Debian-based Operating System. Therefore it uses apt.

The location of sources are at `/etc/apt/sources.list` respectively in the folder `/etc/apt/sources.list.d/`

#### Default Repo:
	deb http://repo.gardenlinux.io/gardenlinux dev main

#### Generally:

	deb http://repo.gardenlinux.io/gardenlinux $days_since_garden_linux_release main

`$days_since_garden_linux_release` is the number of days since 31.03.2020.

For each day since we switched to an own package repository, we offer a respective distribution in our repo.gardenlinux.io apt repository.

While `dev` contains always the latest package versions, the dated-distros contain the packages from that day.


<details>
  <summary>More Info</summary>
  
Try running [bin/garden-version](bin/garden-version), to get the $days_since_garden_linux_release value:
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


