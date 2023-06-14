#!/bin/bash

set -Eexuo pipefail

bucket="$1"
name="$(sed 's/.tar.gz$//g' <<< "$2")"
platform="$(cut -d - -f 1 <<< "$name")"
arch="$(echo "$name" | rev | cut -d - -f 3 | rev)"

mkdir "$name"
tar xzvf "$name.tar.gz" -C "$name"

timestamp="$(date --iso-8601=ns --utc -r "$name/$name.release")"

while IFS='=' read -r key value; do
	declare "$key"="$value"
done < "$name/$name.release"

meta_yml="$(mktemp --suffix=.yaml)"

cat << EOF >> "$meta_yml"
architecture: '$arch'
base_image: null
build_committish: '$GARDENLINUX_COMMIT_ID_LONG'
build_timestamp: '$timestamp'
gardenlinux_epoch: $(bin/garden-version --major "$GARDENLINUX_VERSION")
logs: null
modifiers: [$GARDENLINUX_FEATURES]
platform: '$platform'
published_image_metadata: null
s3_bucket: '$bucket'
s3_key: 'meta/singles/$name'
test_result: null
version: '$GARDENLINUX_VERSION'
paths:
EOF

for file in "$name/$name"*; do
suffix="$(basename "$file" | sed "s/^$name//")"
cat << EOF >> "$meta_yml"
- name: $file
  s3_bucket_name: $bucket
  s3_key: 'objects/$file'
  suffix: $suffix
EOF
done

cat "$meta_yml"

aws s3 cp --recursive "$name" "s3://$bucket/objects/$name"
aws s3 cp --content-type "text/yaml" "$meta_yml" "s3://$bucket/meta/singles/$name"
