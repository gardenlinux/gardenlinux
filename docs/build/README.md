## How does Building Garden Linux work?

By running the build.sh command, you start the Build Process.

This Script generates a Docker Container, which is used as a controlled environment to build Garden Linux with all needed packages and sources. For more information look into the /docker folder


---


The entry point the build.sh script. Possible Arguments are:

### --lessram (default: off)

build will be no longer in memory

### --debug (default: off)

activates basically `set -x` everywhere 

(-x ~= xtrace: Print commands and their arguments as they are executed)


[set manpage linuxcommand.org](https://linuxcommand.org/lc3_man_pages/seth.html)

### --manual (default: off)

build will stop in docker build environment and activate manual mode


The gardenlinux folder is mounted into the docker container at
 

	/opt/gardenlinux
 

You can then progress the build process (as you will also recognize in the log) by running:

	/opt/gardenlinux/bin/garden-build


The manual feature can be used to change e.g. environmental parameters, which are printed by running 

	export

After the Build finishes, you are still inside the docker environment. The outputfolder should be inside your current directory. Just run

	ls output

### --arch  (default: architecture the build runs on)

builds for a specific architecture - currently either "amd64" or arm64

### --suite (default: testing)

specifies the debian suite to build for e.g. bullseye, potatoe

### --skip-tests (default: off)

deactivates tests

### --skip-build (default: off)
	
Does not recreate the docker environment - only use, if you've built Garden Linux successfully at least one time before on this machine

---
	
## Final Output Files

Inside the outputfolder you find a few different files, depending on the included features:

- .raw - this is the raw Image

#### _pxe:

- .squashfs
- .vmlinuz
- .initrd
- 

#### _iso:

- .iso


#### ... :
 
- TODO

---

## Additional Information

---

- TODO: How does BUILD_IMAGE variable in build.sh work?
