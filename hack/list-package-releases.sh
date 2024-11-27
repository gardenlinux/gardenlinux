#!/usr/bin/env bash

set -eufo pipefail

org=gardenlinux

gh api --paginate "/orgs/$org/repos" | jq -r '.[] | .name' | grep '^package-' | grep --invert-match package-build | while read -r repo; do
        TAG_NAME=$(GH_PAGER= gh release view --repo="$org/$repo" --json=tagName --jq='.tagName')
	echo "https://github.com/$org/$repo" $TAG_NAME
done
