## Feature: gcp

<website-feature> This Feature adapts the Garden Linux Build for Google Compute Engine (gce guest environment). </website-feature>

---

	Type: Platform
	Included Features: cloud

#

### Uploading Image to GCP

- create compressed tar image (disk must be called disk.raw)

```tar --format=oldgnu -Sczf compressed-image.tar.gz disk.raw```

- upload tar:

```gsutil cp compressed-image.tar.gz gs://garden-linux-test```


- create image:

```gcloud compute images create garden-linux-gcp-01 --source-uri gs://garden-linux-test/compressed-image.tar.gz```

#
