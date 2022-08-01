# Workflows

## Dev
Runs on `push` and `pull_request` (enabled for branches created by Garden Linux Developer)
1. Build Garden Linux Images

See [dev.yml](dev.yml) for implementation details.

## Nightly
Runs every day (enabled only for main branch):

1. Builds Garden Linux images
2. On successful build, images are uploaded to S3

See [nightly.yml](nightly.yml) for implementation details. 

## Beta Release
Runs weekly on main branch
1. Builds Garden Linux images
1. Build integration test container
1. Runs platform tests for each supported platform 
<!-- 1. On successful tests, images are handed over to Tekton Pipeline for publishing -->
1. Creates git tag `beta-<Major>.<Minor>` (for tested HEAD of main)

See [beta.yml](beta.yml) for implementation details. 

## Stable Release
Runs on push to a release branch (enabled for `stable-**` branches)

Stable branches must be manually created.

1. Builds Garden Linux images
2. Build integration test container
3. Runs platform tests for each supported platform 
4. On successful tests, images are handed over to Tekton Pipeline for publishing

See [stable.yml](stable.yml) for implementation details. 
