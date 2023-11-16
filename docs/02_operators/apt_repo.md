# Garden Linux Repositories

The apt repository is exposed at `repo.gardenlinux.io`.
If you have added the repository to the `/etc/apt/sources.list` or a file in the folder `/etc/apt/sources.list.d/`,
you can search for packets via `apt search`. Searching by opening the url in a webbrowser is currently disabled.

The `repo.gardenlinux.io` repository contains our own packages and a selected set of packages mirrored from `Debian testing`.
Packages are built, signed and deployed via the Garden Linux gitlab pipelines.


| Release  | Line for `/etc/apt/sources.list`  | Description  |
|---|---|---|
| dev  | `deb https://repo.gardenlinux.io/gardenlinux dev main`  | New package versions are publishes here first. |
| `$major.$minor` | `deb https://repo.gardenlinux.io/gardenlinux major.minor main` | Packages for the the Garden Linux version `major.minor`  |


## Versioning
`$major` is the number of days since `31.03.2020`.

For each day since we switched to an own package repository, 
we offer a respective distribution in our repo.gardenlinux.io apt repository.

While `dev` contains always the latest package versions, 
the dated-distros contain the packages from that day.


<details>
  <summary>More Info</summary>
  
Try running [bin/garden-version](../../bin/garden-version), to get the $days_since_garden_linux_release value:
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

    deb https://repo.gardenlinux.io/gardenlinux 730.0 main
	

</details>



