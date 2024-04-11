# Releases

Garden Linux has a diverse ecosystem, comprising cloud and container images, apt repositories, and essential tools like the container toolbelt and NVIDIA driver installer. 

Each release within the Garden Linux ecosystem is accompanied by multiple artifacts. 
These artifacts are made easily discoverable and automatically consumable through an OCI registry. 
This OCI registry contains self-referencing links to related artifacts and adheres to a defined general structure, which is detailed in the following section.



## OCI Artefact Overview

The following sections and diagrams are an abstract representation of artefacts within the OCI registry,
showing the relations between OCI Artefacts and URLs to foreign resources.

### Release
Each release creates multiple products within the Garden Linux ecosystem. 
```mermaid

graph TD;

    Release[Release] --> CloudImages[Cloud Images];
    Release[Release] --> ContainerImages[Container Images];
    Release[Release] --> MetaData[Meta Data];


    MetaData[MetaData] --> Version;
    MetaData[MetaData] --> Changelog;
    MetaData[MetaData] --> Manifest;
    MetaData[MetaData] -->|Foreign Reference| GHReleasePage[GitHub Release Page];
    MetaData[MetaData] -->|Foreign Reference| GardenerToolbelt[Gardener Toolbelt Container];
    MetaData[MetaData] -->|Foreign Reference| NvidiaInstaller[NVIDIA Driver installer];

```


### Cloud Images 
`CloudImages` is an abstract object that references `CloudImage` objects for each supported cloud platform.
`CloudImages` does not necesarily have to be implemented as an object, it can also be a simple list.
The `CloudImage` type defines data for a single cloud image.


```mermaid
graph TD;

    CloudImages[Cloud Images] -->|has many| CloudImage;
    CloudImage[Cloud Image] --> TestLog[Test Logs];
    CloudImage[Cloud Image] --> AuditLogs[Audit Logs];
    CloudImage[Cloud Image] --> LinuxKernel[Kernel];
    CloudImage[Cloud Image] --> KernelCmdLine[Kernel Cmdline];
    CloudImage[Cloud Image] --> rootfs[Rootfs tarball];
    CloudImage[Cloud Image] -->|Foreign Reference| AptRepository[Apt Repository];
    CloudImage[Cloud Image] -->|Foregin Reference| ContainerImages[Container Images];

```



### Container Images

Multiple container images for different purposes exist.
The structure `ContainerImages` is the entry point to discover all available containers for a release.

```mermaid
graph TD;
    ContainerImages[ContainerImages] --> BaseContainer;
    ContainerImages --> BareContainer;
    ContainerImages --> DriverBuildContainer;
    ContainerImages --> PackageBuildContainer;
    ContainerImages --> DebianSnapshotContainer;

    BareContainer[BareContainer] --> BarePython;
    BareContainer --> BareSAPmachine;
    BareContainer --> BareLibc;
    BareContainer --> BareNodejs;
```

# Implementations

## Pure OCI Implementation
See [OCI Implementation specification](oci-implementation-specification.md) for details.

## OCM Implementation 

See [OCM Implementation specification](ocm-implementation-specification.md) for details.


## OCI+OCM hybrid Implementation 

Easy to achieve, since OCM can reference artefacts from OCI. 
If OCI Implementation is selected as first target, a follow up OCM implementation can reference those 
OCI artefacts.


