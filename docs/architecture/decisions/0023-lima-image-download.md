# 23. Providing Garden Linux Images for Lima-VM via Containerized YAML Generator

Date: 2025-11-20

## Status

Accepted

## Context

We want to provide Garden Linux images for Lima-VM in a convenient and user-friendly way. Currently, our pipeline publishes images to S3 buckets without simple or clean URLs, requiring a wrapper to retrieve the image URL. The existing `start-lima.py` script introduces additional dependencies on Python packages, Podman, and a local clone of the Garden Linux git repository. Our goal is to make this a proper feature in the pipeline, avoiding special case handling for Lima-VM where possible.

## Decision

We will build and publish a container image that, when run, outputs YAML suitable for creating Lima VMs based on user-specified parameters. This approach standardizes the process and removes the need for Lima-specific scripts or wrappers.

## Example invocation

```bash
# Without extra parameter, use the latest stable release at the time
podman run -it --rm ghcr.io/gardenlinux/lima | limactl start --name gardenlinux -
# Special parameter to get the current nightly version
podman run -it --rm ghcr.io/gardenlinux/lima nightly | limactl start --name gardenlinux -
# Use a specific release
podman run -it --rm ghcr.io/gardenlinux/lima 2070.0.0 | limactl start --name gardenlinux -
```

The container just writes the yaml to standard output.
The user can redirect this to a file for inspection/editing or directly pipe to lima.

## Consequences

- Users will need Docker or Podman to run the container image.
  - While this is an extra dependency for the user, it is still way less intrusive than requiring a python interpreter, python dependencies and a checkout of the Garden Linux git repo.
- We need to build, publish and update the lima yaml builder container image.
- We eliminate the need for special case handling for Lima-VM, simplifying the workflow and reducing maintenance overhead.
- The process becomes more consistent and easier to use for end users.

## Alternatives considered

- Special pipeline for building lima images
  - We want to avoid this for the sake of pipeline uniformity and simplicity
- Make all published images available at nice urls such as `https://images.gardenlinux.org/[image variant here].raw`
  - This might be a nice next step, not in scope for the current task
