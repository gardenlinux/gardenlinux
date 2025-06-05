#!/bin/bash

set -Eexuo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel)
PATH="${ROOT_DIR}/bin:${PATH}"

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

if grep _usi <<< "$GARDENLINUX_FEATURES" &> /dev/null; then
	usi_feature=true
else
	usi_feature=false
fi

if grep _trustedboot <<< "$GARDENLINUX_FEATURES" &> /dev/null; then
	secboot_feature=true
else
	secboot_feature=false
fi

cat << EOF >> "$meta_yml"
architecture: '$arch'
base_image: null
build_committish: '$GARDENLINUX_COMMIT_ID_LONG'
build_timestamp: '$timestamp'
gardenlinux_epoch: $(garden-version --major "$GARDENLINUX_VERSION")
logs: null
modifiers: [$GARDENLINUX_FEATURES]
platform: '$platform'
require_uefi: $usi_feature
secureboot: $secboot_feature
published_image_metadata: null
s3_bucket: '$bucket'
s3_key: 'meta/singles/$name'
test_result: null
version: '$GARDENLINUX_VERSION'
paths:
EOF

for file in "$name/$name"*; do
suffix="$(basename "$file" | sed "s/^$name//")"
md5sum=$(md5sum -b "$file" | cut -d " " -f 1)         # human readable (hexlified) digest for tags
md5bin=$(openssl md5 -binary "$file" | base64 -w0)    # base64 encoded binary digest for S3 api
sha256sum=$(sha256sum -b "$file" | cut -d " " -f 1)
sha256bin=$(openssl sha256 -binary "$file" | base64 -w0)
cat << EOF >> "$meta_yml"
- name: $file
  s3_bucket_name: $bucket
  s3_key: 'objects/$file'
  suffix: $suffix
  md5sum: $md5sum
  sha256sum: $sha256sum
EOF
object_key="objects/$file"

aws configure set default.s3.multipart_threshold 100MB
aws configure set default.s3.multipart_chunksize 100MB
aws configure set default.s3.max_concurrent_requests 16

aws s3api put-object --body "$file" --bucket "$bucket" --key "$object_key" \
  --content-md5 "$md5bin" --checksum-algorithm sha256 --checksum-sha256 "$sha256bin" \
  --tagging "md5sum=$md5sum&sha256sum=$sha256sum&platform=$platform&architecture=$arch&version=$GARDENLINUX_VERSION&committish=$GARDENLINUX_COMMIT_ID_LONG"
done

cat "$meta_yml"

aws s3 cp --content-type "text/yaml" "$meta_yml" "s3://$bucket/meta/singles/$name"
