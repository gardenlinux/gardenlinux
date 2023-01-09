# Workflows

## Dev
Runs on `push` and `pull_request` (enabled for branches created by Garden Linux Developer)
1. Build Garden Linux Images

See [dev.yml](dev.yml) for implementation details.

## Nightly
Runs every day (enabled only for main branch):

1. Builds Garden Linux images
1. On successful build, images are uploaded to S3

See [nightly.yml](nightly.yml) for implementation details. 

