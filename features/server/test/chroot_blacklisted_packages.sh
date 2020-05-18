#!/usr/bin/env bash

rootfsDir=$1
rc=0

# There should not be blacklisted packeges on the filesystem
echo "checking for blacklisted packeges"
blacklistedPackagesFile="/tmp/blacklisted_packages.txt"
dpkgBin="${rootfsDir}/usr/bin/dpkg"

output=$("${dpkgBin}" -l | grep -wf "${blacklistedPackagesFile}")

if [ -z "${output}" ]
then
      echo "OK - there are no blacklisted packages on the filesystem"
else
      echo "FAIL - he following blacklisted packages were found on the filesystem:"
      echo "${output} | awk '{ print $2 }'"
      rc=1
fi

exit $rc
