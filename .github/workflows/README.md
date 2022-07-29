# Workflows


## Dev
Runs on `push` and `pull_request` (enabled for branches created by Garden Linux Devs)
1. Build Garden Linux Images

See [dev.yml](dev.yml) for implementation details.


## Nightly
Runs every day (enabled only for main branch):

1. Builds Garden Linux images
2. Build integration test container
3. Runs platform tests for each supported platform 
4. On successfull tests, images are handed over to Tekton Pipeline for publishing

See [nightly.yml](nightly.yml) for implementation details. 


