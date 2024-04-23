# OCI Implementation Specification


## Implementation Details

The [oci image-spec](https://github.com/opencontainers/image-spec) describes the standardized oci image format. 
We utilize this specification to upload any Garden Linux artefact as we design. 

The following sub-sections describe how we utilize the oci-image format to achieve the concepts mentioned above to implement the structure defined in the [HLD](high-level-design).

## Graph Overview
The following diagram shows the general hierachical structure of the OCI registry. We will go through each component and its implementation details in respective sub-sections in this document.

```mermaid
graph LR;
    root_index[oci-index: root]--> platform_index_aws[oci-index: aws];
    root_index--> platform_index_ali[oci-index: ali];
    root_index--> platform_index_azure[oci-index: azure];
    root_index--> platform_index_gcp[oci-index: gcp];
    root_index--> platform_index_openstack[oci-index: openstack];
    root_index--> platform_index_khost[oci-index: khost];
    root_index--> base_container_manifest[oci-manifest: container base image];

    platform_index_aws--> aws_manifest_1[amd64 artefact];
    platform_index_aws--> aws_manifest_2[amd64 artefact];
    
    aws_manifest_1[oci-manifest: featureset 1]--> aws_image_1_arm64;
    aws_manifest_1--> aws_image_1_amd64[oci-image: AMD64];
    aws_manifest_2[oci-manifest: featureset 2]--> aws_image_2_arm64[oci-image: ARM64];
    aws_manifest_2--> aws_image_2_amd64[oci-image: ARM64];

    aws_image_1_arm64[oci-image: AMD64]--> layer_rootfs[layer: rootfs];
    aws_image_1_arm64--> layer_cmdline[layer: cmdline];
    aws_image_1_arm64--> layer_kernel[layer: kernel];
```

### Component: root oci-index
The root oci-index holds a list of references to `oci-index: platform` and `oci-manifest` type objects.
We specify the properties of the `oci-index: root` in the table below.

Conceptually, `oci-index: root` contains all platforms for an OS. 
An OS has a defined release-cycle, but could contain multiple flavors for different user groups.

For the sake of readability, we assume for the rest of this spec, that the OS is gardenlinux/gardenlinux, but this could be extended to other OS images build with the gardenlinux/builder, for example gardenlinux/gardenlinux-cc.

| oci-index property Name  | Property Value                               | Property Description                                                                                       |
|----------------|----------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| `schemaVersion`| `2`                                          | This is REQUIRED to bne set to `2`.                                                                        |
| `mediaType`    | `application/vnd.oci.image.index.v1+json`    | Sets the type to be an oci index                                                                           |
| `manifests`    | See table [index manifests](#index-manifests)                    | Array of Manifests of mediatype manifest or (potentially) index. Each object in this array includes a set of descriptor propteries. |
| `annotations`  | See table  [index-annoations](#index-manifest-annotations) | An optional set of key-value pairs for additional metadata about the image index.                          |


#### oci-index property: manifest list

The oci-index contains an array of manifests, where each manifest object in that array contains the information described in the table below.
Please note that these properties are for the list object, not the oci-manifest properties. The oci-manifest properties are described later.

| Manifest Object Property Name            | Property Value                           |
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



#### oci-index property: manifest-annotations 

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

### oci-index: Platform
A platform could contain multiple flavors, for example `khost-gardener`, `khost`, `khost_pxe` and `khost_dev`.
As opposed to a flat `oci-index: root` containing all platform manifests, this spec defines that
a child node called `oci-index: platform` is introduced, that is referenced by the `oci-index: root` and references all `oci-manifest: flavor`.

### oci-manifest: flavor
A Garden Linux image can come in different CPU architecture types.
The platform manifest lists all architecture specific oci images for a given platform. 


See also [oci image spec: manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
### oci-image:  Cloud Image


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


#### oci-image property: annotations

### Image - Container

Podman/Docker clients understand the index and find the Base Container manifest. 
This enables users to use podman/docker and use the OCI package just as they would use any other oci image.
```
    podman pull ghcr.io/gardenlinux/gardenlinux:1443.3
```


## Links
* [oci image spec: layer](https://github.com/opencontainers/image-spec/blob/main/layer.md)
* [oci image spec: manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
* [oci image spec: annotations](https://github.com/opencontainers/image-spec/blob/main/annotations.md)
* [oci image spec: descriptors](https://github.com/opencontainers/image-spec/blob/main/descriptor.md)


