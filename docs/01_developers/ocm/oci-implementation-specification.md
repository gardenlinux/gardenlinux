# OCI Implementation Specification


## Implementation Details

The [oci image-spec](https://github.com/opencontainers/image-spec) describes the standardized oci image format. 
We utilize this specification to upload any Garden Linux artefact as we design. 

The following sub-sections describe how we utilize the oci-image format to achieve the concepts mentioned above to implement the structure defined in the [HLD](high-level-design).


### Index

```mermaid
graph LR;

    Index[Index of gardenlinux/gardenlinux:version]--> ALI[Ali - OCI Manifest];
    Index[Index of gardenlinux/gardenlinux:version]--> AWS[aws - OCI Manifest];
    Index[Index of gardenlinux/gardenlinux:version]--> AZURE[Azure - OCI Manifest];
    Index[Index of gardenlinux/gardenlinux:version]--> metal[Metal - OCI Manifest];
    Index[Index of gardenlinux/gardenlinux:version]--> OPENSTACK[OpenStack - OCI Manifest];
    Index[Index of gardenlinux/gardenlinux:version]--> Container[Base Container- OCI Manifest];
    
```

### Cloud images
The index described previously links all supported Garden Linux image platform manifests, where a platform manifest is structured as described in the following diagram:

```mermaid
graph LR;

    cloud_image_amd64[Platform Manifest]--> layer_rootfs[layer: rootfs];
    cloud_image_amd64--> layer_kernel[layer: kernel];
    cloud_image_amd64--> layer_cmdline[layer cmdline];
    cloud_image_amd64--> layer_changelog[layer: changelog];
    cloud_image_amd64--> layer_testlog[layer: testlog];
```    


### Base Container

Podman/Docker clients understand the index and find the Base Container manifest. 
This enables users to use podman/docker and use the OCI package just as they would use any other oci image.
```
podman pull ghcr.io/gardenlinux/gardenlinux:1443.3
```

```mermaid
graph LR;

    Manifest[Manifest of base container]--> artifact_amd64[amd64 artefact];
    Manifest[Manifest of base container]--> artifact_arm4[arm64 artefact];
```    



## Links
* [oci image spec: layer](https://github.com/opencontainers/image-spec/blob/main/layer.md)
* [oci image spec: manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
* [oci image spec: annotations](https://github.com/opencontainers/image-spec/blob/main/annotations.md)
* [oci image spec: descriptors](https://github.com/opencontainers/image-spec/blob/main/descriptor.md)


