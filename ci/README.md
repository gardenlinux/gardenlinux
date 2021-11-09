# Introduction
The following section describes how Garden Linux can be built using a pipeline.
The open source project [Tekton](https://github.com/tektoncd/pipeline) is used as environment to run the build. The build pipeline is fully containerized and requires a Kubernetes cluster.

## Overview About The Build
The Garden Linux build is done in several phases and runs fully containerized. In the first phase some images are created that are used as base images for the subsequent build steps. The second phase builds several packages and the Linux kernel. The third phase build the VM images using the packages from step 2 and standard Debian packages. The final VM images are uploaded to an (S3-like) object store and can optionally be uploaded to hyperscalers (Alicloud, AWS, Azure or Google).

## Installation
You have to install Tekton pipelines and the Tekton dashboard (recommended)

Tekton pipelines:
[https://github.com/tektoncd/pipeline/releases](https://github.com/tektoncd/pipeline/releases)

`kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/previous/v0.25.0/release.yaml`

Install Tekton dashboard (check compatibility with Tekton pipelines release):
[https://github.com/tektoncd/dashboard/releases](https://github.com/tektoncd/dashboard/releases)

`kubectl apply --filename https://github.com/tektoncd/dashboard/releases/download/v0.18.0/tekton-dashboard-release.yaml`

`http://localhost:9097`

Install Python (>= 3.8) and pip
Install Python libraries
`pip install -r ci/requirements.txt`

Install

```
kubectl (installed automatically from script)
tekton-cli (installed automatically from script)
```

### Set Limits
The build machine requires a certain amount of resources usually not available by default. Apply the
following limits:

```
apiVersion: v1
kind: LimitRange
metadata:
  name: gardenlinux
spec:
  limits:
  - type: Container
    max:
      ephemeral-storage: 128Gi
    min:
      ephemeral-storage: 16Gi
    default:
      ephemeral-storage: 128Gi
      memory: 24G
      cpu: 16.0
    defaultRequest:
      ephemeral-storage: 20Gi
      memory: 4G
      cpu: 1.0

```

### Grant API Permissions To Script User
All tekton related scripts are executed by a service user "default" in the corresponding namespace. This user must be granted the permission to get (read) access to Tekton and pod resources:

```
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: incluster-tektonaccess
rules:
- apiGroups: ["tekton.dev"]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: incluster-tektonaccess-gardenlinux
subjects:
- kind: ServiceAccount
  name: default
  namespace: gardenlinux
roleRef:
  kind: ClusterRole
  name: incluster-tektonaccess
  apiGroup: rbac.authorization.k8s.io
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: incluster-tektonaccess-jens
subjects:
- kind: ServiceAccount
  name: default
  namespace: jens
roleRef:
  kind: ClusterRole
  name: incluster-tektonaccess
  apiGroup: rbac.authorization.k8s.io
```

### Namespace:

The namespace can be set according to your preferences. In this document and in the provided scripts the namespace "gardenlinux" is used. The namespace is set in an environment variable "GARDENLINUX_TKN_WS". If not set it defaults to "gardenlinux"

### Overview About The Build

The Garden Linux build is done in several phases and runs fully containerized. In the first phase some images are created that are used as base images for the subsequent build steps. The second phase builds several packages and the Linux kernel. The third phase build the VM images using the packages from step 2 and standard Debian packages. The final VM images are uploaded to an (S3-like) object store and can optionally be uploaded to hyperscalers (Alicloud, AWS, Azure or Google).

The build uses two pipelines: One to build the packages and one to build the VM images. Package builds are time consuming and resource intensive. A package build needs at least 70GB of disk space and takes >4h to build on a typical build machine.

Build variants:
The build can handle various variants of build artifacts. These are configured by a flavour set. The flavours are defined in the file flavours.yaml in the root directory of th Git repository. By default there is one set in this file named "all". You can add more sets according to your needs.

Build-Target:
There are options how the build artifacts are handled after build. This is set in the environment variable BUILD_TARGETS (see also class BuildTarget in ci/glci/model.py). Currently there are four variants supported:

 - `build`
 - `manifest`
 - `release`
 - `publish`

If the variable is not set it defaults to "`build`"

The flavour set build by the pipeline is contained in the environment variable FLAVOUR_SET and defaults to "all" if not set.

**Example:**
Here is example to build nly the AWS image. Append the following snippet to `flavours.yaml`:

```
  - name: 'aws'
    flavour_combinations:
      - architectures: [ 'amd64' ]
        platforms: [ aws ]
        modifiers: [ [ _prod, gardener ] ]
        fails: [ unit, integration ]

```

### Environment Variables
The script to generate the pipeline definitions reads various environment variables. These variables can be set to control the configuration. See also file [ci/lib.sh](lib.sh). Here is an example:

```
# Namespace where pipelines are deployed defaults to "gardenlinux":
export GARDENLINUX_TKN_WS=gardenlinux
# type of artifacts to be built:
export BUILD_TARGETS=manifests
# build variant: defaults to "all"
export FLAVOUR_SET=all
# Git branch to build, defaults to "main"
export BRANCH_NAME=main
# path to upload base images in container registry
export OCI_PATH=eu.gcr.io/gardener-project/test/gardenlinux-test
# Repository in Git:
export GIT_URL=https://github.com/gardenlinux/gardenlinux
# secret encryption, set algorithm to "PLAINTEXT"
export SECRET_CIPHER_ALGORITHM=PLAINTEXT
```

### Creating and running the pipelines

Run the script to generate and apply the pipelines:

`ci/render_pipelines_and_trigger_job`

This script creates several yaml files containing the Tekton definitions for the gardenlinux build. They are applied automatically to the target cluster described by your `KUBECONFIG` environment variable.

This script has the following parameters:

* `--image-build`: Build Garden Linux
* `--package-build`: Build the packages
* `--wait`: The script terminates when pipeline run is finished

Example:

`ci/render_pipelines_and_trigger_job --image-build`


### Credential Handling

The build pipeline can be used with a central server managing configuration and secrets. As an alternative all credentials can be read from a Kubernetes secret named "secrets" in the corresponding namespace. This secret will be automatically generated from configuration files. The switch between central server and a Kubernetes secret is done by an environment variable named `SECRET_SERVER_ENDPOINT`. If it is not set the secret will be generated and applied. At minimum there need to be two secrets: One for uploading the artifacts to an S3-like Object store and one to upload container images to an OCI registry. Example files are provided in the folder `ci/cfg`.

Edit the files cfg/cfg_types.yaml. Each top-level entry refers to another file
containing the credentials. Examples with templates are provided. A second entry is for uploading the base-image and to an OCI registry. Additional configuration information is found in [cicd.yaml](cicd.yaml)

For sending notifications by default recipients are read from the CODEOWNERS files. Resolving this to email requires access to the Github API which is not possible for external users. The behavior can be overriden by setting the variable `only_recipients` in the pipelineRun file. If this variable contains a semicolon separated list of email addresses emails are sent only to these recipients. CODEWONWERS access is not needed then. For configuring an SMTP server a sample file is provided.


## Integration Tests (under construction)

The integration test are implemented as their own tekton task which can be
found [here](./integrationtest-task.yaml).  The test automatically clones the
github repo specified in the tekton resource and executes the integration test
with the specified version (branch or commit).

The task assumes that there is a secret in the cluster with the following
structure:

```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: github-com-user
  annotations:
    tekton.dev/git-0: https://github.com
type: kubernetes.io/basic-auth
stringData:
  username: <github username>
  password: <github password>
```

The test can be executed within a cluster that has tekton installed by running:

```
# create test defintions and resrouces
kubectl apply -f ./ci/integrationtest-task.yaml

# run the actual test as taskrun
kubectl create -f ./ci/it-run.yaml
```
Running the integration tests is work-in-progress.