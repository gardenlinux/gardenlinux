## Manually triggered Workflows

| Name                                                                 | When/Why to Use                                                       | Side Effects                                                       |
|----------------------------------------------------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------|
| [manual_release](../../.github/workflows/manual_release.yml)               | Use when you need to manually trigger a release build.                | Link to S3 bucket `gardenlinux-github-releases`.      |
| [manual_tests](../../.github/workflows/manual_tests.yml)                   | Use to perform platform tests, build a specific version, or download images from S3. | If specified, builds image and puts it in S3 `gardenlinux-github-releases` bucket. |
| [manual_gh_release_page](../../.github/workflows/manual_gh_release_page.yml) | Use to create a new GitHub release page for a published Garden Linux release. | Creates a new GitHub release page on `gardenlinux/gardenlinux`. |
| [manual_tag_latest_container](../../.github/workflows/manual_tag_latest_container.yml) | Use when you need to manually tag a container image as `latest`. You could also do this locally without this workflow.       | Tags the given container image as `latest`.  |
| [publish](../../.github/workflows/publish.yml)   | Use to publish containers after a successful `nightly`, or successful `manual_release`. Can be triggered manually to publish based on a specific `run_id`.           | Publishes container images to ghcr.io |
| [publish_s3](../../.github/workflows/publish_s3.yml)    | Use to publish artifacts to S3 after a successful `nightly`, or successful `manual_release`. Can be triggered manually to publish based on a specific `run_id`.           | Publishes artifacts to S3 `gardenlinux-github-releases` bucket. |
| [cloud_test_cleanup](../../.github/workflows/cloud_test_cleanup.yml) | Use to clean up cloud resources used during platform tests.           | Removes cloud resources used to perform platform tests. |

## Scheduled Workflows

| Name                                                                 | Schedule  | Description                                                                 | Side Effects                                                       |
|----------------------------------------------------------------------|-----------|-----------------------------------------------------------------------------|--------------------------------------------------------------------|
| [nightly](.github/workflows/nightly.yml)                             | Daily    | Builds and platform tests the current version from the main branch using the current apt repo of the day. Uploads .0 release candidate of the day to S3. | Uploads .0 release candidate of the day to S3 `gardenlinux-github-releases` bucket. |
| [cloud_test_cleanup](.github/workflows/cloud_test_cleanup.yml) | Daily    | Cleans up accumulated cloud resources spawned via Open Tofu in platform tests. | Removes cloud resources used to perform platform tests. |
