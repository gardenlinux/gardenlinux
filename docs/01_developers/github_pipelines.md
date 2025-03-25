## Manually triggered Workflows 


| Name                                                                 | When/Why to Use                                                       | Side Effects                                                       |
|----------------------------------------------------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------|
| [manual_release](.github/workflows/manual_release.yml)               | Use when you need to manually trigger a release build.                | Side effect: Link to S3 bucket `gardenlinux-github-releases`.      |
| [manual_tests](.github/workflows/manual_tests.yml)                   | Use to perform platform tests, build a specific version, or download images from S3. | Side effects: If specified, builds image and puts it in S3 `gardenlinux-github-releases` bucket. |
| [manual_gh_release_page](.github/workflows/manual_gh_release_page.yml) | Use to create a new GitHub release page for a published Garden Linux release. | Side effect: Creates a new GitHub release page on `gardenlinux/gardenlinux`. |
| [publish](.github/workflows/publish.yml)                             | Use to publish artifacts to S3 after a successful build.               | Side effects: Publishes artifacts to S3 `gardenlinux-github-releases` bucket. |
| [publish_s3](.github/workflows/publish_s3.yml)                       | Use to upload artifacts to S3 from a specific `run_id`.                | Side effects: Uploads given `run_id` to `gardenlinux-github-releases` bucket. |
| [nightly](.github/workflows/nightly.yml)                             | Use for daily builds to generate the version of the day and upload it as a release candidate. | Side effects: Uploads .0 release candidate of the day to S3 `gardenlinux-github-releases` bucket. |
| [platform_test_cleanup.yml](.github/workflows/platform_test_cleanup.yml) | Use to clean up cloud resources used during platform tests.           | Side effects: Removes cloud resources used to perform platform tests. |
| [tag_latest_container_manually](.github/workflows/tag_latest_container_manually.yml) | Use when you need to manually tag a container image as `latest`.        | Side effects: Tags the given container image as `latest`.          |



## Scheduled Workflows

| Name                                                                 | Schedule  | Description                                                                 | Side Effects                                                       |
|----------------------------------------------------------------------|-----------|-----------------------------------------------------------------------------|--------------------------------------------------------------------|
| [nightly](.github/workflows/nightly.yml)                             | Daily    | Builds and platform tests the current version from the main branch using the current apt repo of the day. Uploads .0 release candidate of the day to S3. | Side effects: Uploads .0 release candidate of the day to S3 `gardenlinux-github-releases` bucket. |
| [platform_test_cleanup.yml](.github/workflows/platform_test_cleanup.yml) | Daily    | Cleans up accumulated cloud resources spawned via Open Tofu in platform tests. | Side effects: Removes cloud resources used to perform platform tests. |


