tekton pipelines for gardenlinux
================================

This directory contains [Tekton](https://github.com/tektoncd/pipeline) resource definitions that
exhibit a similar behaviour as previously implemented using GitHub Actions.

Configuration is somewhat redundant to the one in `Makefile`. The build pipeline currently
assumes that there is a prebuilt container image. It also assumes to be run in a k8s cluster
with a (Gardener-CICD-proprietary) "SecretsServer".

There are, of course, still open issues:

- resources should be templatified
  - hardcoded cfg should be injected
- build image should also be built using tkn
- react on head-updates / offer release job semantics
- apply different repository layout
- error handling / notification (e.g. mark PRs/commits as good or broken)
- offer some UI
