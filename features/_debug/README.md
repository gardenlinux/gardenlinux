## Feature _debug

### Description
<website-feature>
This flag adds a debug container to the image. In the case the image is immutable and additional software is needed for debugging purposes, the debug container offers a writable environment to debug the system, it has access to the host network and mounts all system relevant files and directories.
</website-feature>

It adds a script to spawn a container, the script pulls a Debian slim container and installs the `openssh-server` and starts the container with the `sshd` running on port 22. Make sure the host system is not running a `sshd` instance. Alternatively the script can create a container from a local archive or pull a container from an external registry, in this cases the container will not be modified by the script. Also two systemd services are installed to create and start the container a boot time of the host system.

### Usage
By default the Debian slim container is pulled and `openssh-server` is installed in the container before it is started. The defaults can be changed in the config file `/etc/debugbox.conf`.

- **IMAGE** defaults to `debugbox`, if a registry is set, it should contain the name of the image to pull
- **REGISTRY** default is empty, sets the registry to pull an external image from
- **CONTAINER_ARCHIVE** default is empty, if set it should be the full path to a locally available container archive to create the container from.
- **CMD** defaults to `/usr/sbin/sshd -D`, the command that is executed in the container
