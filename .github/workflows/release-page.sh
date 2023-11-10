#!/bin/bash

set -Eeufo pipefail
set -x
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION

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
		commit="$1"; shift
		name="$1"; shift
		commit_short=${commit:0:8}
		body="$(.github/workflows/generate_release_note.py generate --version "$name" --commitish "$commit_short" --escaped)"
		# If release does not exist, this get request will return a 404
		release="$(get "releases/tags/$tag" | jq -r '.id' || true)"
		[ ! "$release" ] || delete "releases/$release"

		# Only main branch can post requests, otherwise will return a 403
		release="$(post "releases" '{
			"tag_name": "'"$tag"'",
			"target_commitish": "'"$commit"'",
			"name": "'"$name"'",
			"body": "'"$body"'",
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
