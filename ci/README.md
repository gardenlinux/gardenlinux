tekton pipelines for gardenlinux
================================

This directory contains [Tekton](https://github.com/tektoncd/pipeline) resource definitions for
CICD Build and Test Pipelines for gardenlinux.

The build pipeline assumes to be run in a k8s cluster with a
(Gardener-CICD-proprietary) "SecretsServer".

There are, of course, still open issues:

- resources should be templatified
  - hardcoded cfg should be injected
- build image should also be built using tkn
- release job semantics
- error handling / notification (e.g. mark PRs/commits as good or broken)


## Integration tests

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

Although the AWS tests are working, there are still some open points.
- GCP tests do not work correctly, due to issues regarding ssh into the machines.
- GCP and AWS images are currently hardcoded. For the future pipline, we need to upload the images in a previous step and use the newly upladed dev images.
-
