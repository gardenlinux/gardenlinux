#!/bin/bash

set -Eeufo pipefail

bucket="$1"
prefix="$2"

mkdir "$prefix"

s3_yaml_url="s3://$bucket/meta/singles/$prefix"

aws s3 cp "$s3_yaml_url" - \
| podman run --rm -i mikefarah/yq '.paths[] | "s3://" + .s3_bucket_name + "/" + .s3_key' \
| while read -r s3_object_url; do
	aws s3 cp "$s3_object_url" "$prefix/$(basename "$s3_object_url")"
done
