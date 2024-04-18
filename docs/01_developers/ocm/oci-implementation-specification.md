# OCI Implementation Specification


## Implementation Details

The [oci image-spec](https://github.com/opencontainers/image-spec) describes the standardized oci image format. 
We utilize this specification to upload any Garden Linux artefact as we design. 

The following sub-sections describe how we utilize the oci-image format to achieve the concepts mentioned above to implement the structure defined in the [HLD](high-level-design).


### Image-Index

The image-index lists multiple manifests, designed to support multiple platforms.
We utilize the image-index to reference all garden linux platforms, including various cloud platforms, metal and container images.


```mermaid
graph LR;

    Index[oci-index: gardenlinux/gardenlinux:version]--> ALI[Ali - OCI Manifest];
    Index--> AWS[oci-manifest: platform aws];
    Index--> AZURE[oci-manifest: platform azure];
    Index--> ALI[oci-manifest: platform Ali];
    Index--> GCP[oci-manifest: platform GCP];
    Index--> OPENSTACK[oci-manifest: platform openstack];
    Index--> OPENSTACK_BAREMETAL[oci-manifest: platform openstack bare metal];
    Index--> CONTAINER[oci-manifest: container base image];
    
```

| Property Name  | Property Value                               | Property Description                                                                                       |
|----------------|----------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| `schemaVersion`| `2`                                          | This is REQUIRED to bne set to `2`.                                                                        |
| `mediaType`    | `application/vnd.oci.image.index.v1+json`    | Sets the type to be an oci index                                                                           |
| `manifests`    | See table index-manifests                    | Array of Manifests of mediatype manifest or (potentially) index. Each object in this array includes a set of descriptor propteries. |
| `annotations`  | See table index-annoations                   | An optional set of key-value pairs for additional metadata about the image index.                          |



#### index-manifests

The index contains an array of manifests, where each manifest object in that array contains the following information described in the table below:

| Property Name            | Property Value                           |
|--------------------------|------------------------------------------|
| `mediaType`              | See Platform Media Types                 |
| `platform`               | Object                                   |
| `platform.architecture`  | CPU architecture type              |
| `platform.variant`       | CPU architecture variant [see](https://github.com/opencontainers/image-spec/blob/main/image-index.md#platform-variants)                       |
| `platform.os`            | Garden Linux                             |
| `platform.os.version`    | Full Garden Linux Version                |
| `platform.os.features`   | NOT USED by Garden Linux.             |
| `platform.features`      | NOT USED by Garden Linux              |
| `annotations`            | See list of index-manifest-annotations  |


#### index-manifest-annotations 

| Key                       | Value                     |
|---------------------------|---------------------------|
| `org.opencontainers.image.version` | Garden Linux Version                 |
| `org.opencontainers.image.title`   | Garden Linux cname (may change, cname just as a description for humans)       |
| `org.opencontainers.image.description` | Short description  |
| `org.opencontainers.image.authors` | `@gardenlinux/garden-linux-maintainers` |
| `org.gardenlinux.cname`            |  Garden Linux cname (can be used for automation)        |
| `org.gardenlinux.builder.version`  | Reference to builder version        |
| `org.gardenlinux.apt.version`  | Reference to apt repository version (the apt distribition used)  |


See also [oci image spec: image-index](https://github.com/opencontainers/image-spec/blob/main/image-index.md)

### Platform Manifest
A Garden Linux image can come in different CPU architecture types.
The platform manifest lists all architecture specific oci images for a given platform. 

```mermaid
graph LR;

    pmanifest[oci-manifest: platform]--> image_arm64[oci-image: arm64 image];
    pmanifest--> image_amd64[oci-image: amd64 image];
```    

See also [oci image spec: manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
### Image - Cloud Image
```mermaid
graph LR;

    image[oci-image: cloud image]--> layer_rootfs[layer: rootfs];
    image[oci-image: cloud image]--> layer_cmdline[layer: cmdline];
    image[oci-image: cloud image]--> layer_kernel[layer: kernel];
    image[oci-image: cloud image]--> layer_changelog[layer: changelog];
    image[oci-image: cloud image]--> layer_testlog[layer: testlog];
```    


| Property Name      | Property Value                          |
|--------------------|-----------------------------------------|
| `schemaVersion`    | 2 |
| `mediaType`        | MIME type string                        |
| `config`           | Object                                  |
| `config.mediaType` | String                                  |
| `config.size`      | Integer                                 |
| `layers`           | Array of layer objects                  |
| `layers[].mediaType` | String                                |
| `layers[].size`      | Integer                               |
| `annotations`      | See list of manifest-annotations  |


#### manifest-annotations

### Image - Container

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


