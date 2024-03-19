## Feature: gcp
### Description
<website-feature>
This platform feature creates an artifact for the Google Cloud Platform.
</website-feature>

### Features
This feature creates a GCP compatible image artifact as an `.raw` file.

To be platform complaint smaller adjustments like defining the platform related clocksource config, networking config etc. are done.
The artifact includes `cloud-init` and `amazon-ec2-utils` for orchestrating the image.

### Uploading Image to GCP

- create compressed tar image (disk must be called disk.raw)

```tar --format=oldgnu -Sczf compressed-image.tar.gz disk.raw```

- upload tar:

```gsutil cp compressed-image.tar.gz gs://garden-linux-test```

- create image:

```gcloud compute images create garden-linux-gcp-01 --source-uri gs://garden-linux-test/compressed-image.tar.gz```

### Unit testing
This platform feature supports unit testing and is based on the `gcp` fixture to validate the applied changes according its feature configuration.

### Meta
|||
|---|---|
|type|platform|
|artifact|`.raw`|
|included_features|cloud|
|excluded_features|None|
