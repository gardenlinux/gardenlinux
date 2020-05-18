#!/usr/bin/env bash

rootfsDir=$1
rc=0

# service accounts should no have shells
echo "checking service accounts for shell"
usersFile="${rootfsDir}/etc/passwd"
declare -a stringsToExclude=("sync")

output=$(awk -F: '$3 > 0 && $3 < 1000 && $7 !~ /\/nologin$/ && $7 !~ /\/false$/ { print $0 }' "${usersFile}")

for stringToExclude in ${stringsToExclude=}
do
      output=$(echo "${output}" | sed "/$stringToExclude/d")
done

if [ -z "${output}" ]
then
      echo "all service accounts have no shells"
else
      echo "there is shell configured in the following service accounts:"
      echo "${output}"
      rc=1
fi

exit $rc

