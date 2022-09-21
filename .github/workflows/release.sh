#!/bin/bash

set -Eeufo pipefail

token="$1"; shift
repo="$1"; shift

curl_path="$(which curl)"

function curl {
	$curl_path -f -u "token:$token" "$@"
}

function get {
	[ $# = 1 ]
	curl -X GET "https://api.github.com/repos/$repo/$1"
}

function post {
	[ $# = 2 ]
	curl -X POST "https://api.github.com/repos/$repo/$1" --data "$2"
}

function delete {
	[ $# = 1 ]
	curl -X DELETE "https://api.github.com/repos/$repo/$1"
}

function upload {
	[ $# = 1 ]
	curl -X POST -H "Content-Type: application/octet-stream" "https://uploads.github.com/repos/$repo/$1" --data-binary @-
}

action="$1"; shift

case "$action" in
	"create")
		tag="$1"; shift
		name="$1"; shift

		release="$(get "releases/tags/$tag" | jq -r '.id' || true)"
		[ ! "$release" ] || delete "releases/$release"

		release="$(post "releases" '{
			"tag_name": "'$tag'",
			"name": "'$name'",
			"body": "auto release, created by GitHub action",
			"prerelease": true
		}' | jq -r '.id')"

		echo "$release"

		;;
	"upload")
		release="$1"; shift

		while read asset_file; do
			asset_name="$(basename "$asset_file")"
			upload "releases/$release/assets?name=$asset_name" < "$asset_file" > /dev/null
			echo "uploaded $asset_file to $release"
		done

		;;
esac
