# Garden Linux Bare Container Documentation

TODO: 
- alpine container images are not posix compliant (add link) comparision
- distroless based on debian stable - we are based on gardenlinux, which is based on testing (add link)
- better introduction
    - explain that it is like GL based on minimal debian
    - hardened agaisnt SAP security guidelines (including protecode scan)
    - ldd-tree dependency minimization
    - super extra small
    - up to date
- workflow model
    - start with a normal container
    - develop like you would normaly
    - install what you need (e.g. openssl, whatnot)
    - build application (build dependencies may be installed by dev)
    - debugging and testing
    - if you are happy with all convinience ...(?)... then you can run unbase_oci
    - all the dependencies you need are there (you propably need to include language specific code files (?) )
    - static testing
    - => result is a container similiar to distroless without maintaining versions of dependent libs, because implicitly done

## Overview
Garden Linux offers a range of specialized bare container images, each tailored for specific applications and designed for minimalism and security:

- **Bare-libc**: Ideal for C/C++ applications requiring only essential C runtime libraries.
- **Bare-python**: Equipped with Python runtime, perfect for Python-based applications.
- **Bare-sapmachine**: Customized for sapmachine with necessary libraries and binaries.
- **Bare-nodejs**: Includes Node.js environment, suitable for server-side JavaScript applications.

These containers are optimized as base images for Dockerfiles. 
Their development is streamlined by the [unbase_oci](https://github.com/gardenlinux/unbase_oci) tool, which efficiently minimizes image size by removing unnecessary components from base container images.


### Unbase OCI Tool
The `unbase_oci` tool is instrumental in the development of these "bare" container images. 

- **Functionality**:
  - Strips unnecessary components from base container images.
  - Reduces image size and potential security vulnerabilities.
  - Operates on OCI archives, comparing base and target images to identify and retain only necessary additions and their dependencies.
- **Repository Link**: [unbase_oci](https://github.com/gardenlinux/unbase_oci)
- **Impact**: This tool is pivotal in creating streamlined, "distroless-like" images, ensuring that the resulting containers are lean and secure.

### Bare-libc
A streamlined container image for applications that need only the basic C library.
- **Features**:
  - Includes essential C runtime libraries.
  - Suited for C/C++ applications with minimal dependencies.
  - Enhanced security through a minimal attack surface.
- **Container Link**: [bare-libc](https://github.com/orgs/gardenlinux/packages/container/package/gardenlinux%2Fbare-libc)

### Bare-python
Optimized for Python applications, this image provides the Python runtime.
- **Features**:
  - Contains the Python interpreter and necessary libraries.
  - Ideal for Python-based applications.
  - Designed for improved security and efficiency.
- **Container Link**: [bare-python](https://github.com/orgs/gardenlinux/packages/container/package/gardenlinux%2Fbare-python)
- **Usage in Dockerfile**:
  ```Dockerfile
  FROM ghcr.io/gardenlinux/gardenlinux/bare-python:nightly
  COPY hello.py /
  CMD ["python", "/hello.py"]
  ```

### bare-sapmachine
Customized for SAP applications, ensuring compatibility and optimized performance.
- **Features**:
  - Necessary libraries and binaries for SAP included.
  - Optimized for sapmachine.
  - Security-focused design.
- **Container Link**: [bare-sapmachine](https://github.com/orgs/gardenlinux/packages/container/package/gardenlinux%2Fbare-sapmachine)

### Bare-nodejs
A container tailored for Node.js applications, providing the Node.js runtime.
- **Features**:
  - Includes Node.js environment.
  - Suitable for server-side JavaScript applications.
  - Minimized footprint for enhanced security and performance.
- **Container Link**: [bare-nodejs](https://github.com/orgs/gardenlinux/packages/container/package/gardenlinux%2Fbare-nodejs)


## Support and Contributions

If you need support or wish to contribute to the development of the "bare" flavor containers, including the `unbase_oci` tool, please refer to the following resources:

- **General Issues and Contributions**: For issues specific to the "bare" containers or to contribute to Garden Linux, visit the [Garden Linux GitHub Repository](https://github.com/gardenlinux/gardenlinux/pulls).
- **Specific Container Repositories**: For detailed information or contributions to individual containers, explore their respective GitHub repository pages linked in their descriptions above.

Your contributions and feedback are valuable in improving these specialized containers and tools.
