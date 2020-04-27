#!/usr/bin/env bash

export TZ="UTC"
export LC_ALL="C"

apt-get update > /dev/null
apt-get install -y --no-install-recommends debsums > /dev/null

echo "testing the integrity of the files from installed packages"
if out=$(debsums -l); then
	echo "OK - verifying if all installed packages provide md5sums"
else
	echo "the following packages don't have md5sums:"
	echo "$out"
	rc=1	
fi
out=$(debsums -sc | grep -vf /tmp/debsums_exclude)
if [ -z "$out" ]; then
	echo "OK - verifying if there are any changed files"
else
	echo "FAIL - the following files have changes:"
	echo "$out"
	rc=1
fi
exit $rc
