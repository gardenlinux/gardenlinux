#!/usr/bin/env bash

rootfsDir=$1
rc=0

# There should not be world-writable strings in path
echo "check for world-writable strings in path"
rootBashProfileFile="${rootfsDir}/root/.bashrc"
homeBashProfileFile="${rootfsDir}/home/dev/.bashrc"
rootPath=$(grep "PATH=" "${rootBashProfileFile}")
homePath=$(grep "PATH=" "${homeBashProfileFile}")

check_path () {
   result=0;

   for dir in ${1//:/ }; do
    [ -L "${rootfsDir}/${dir}" ] && printf "%b" "symlink, "
    if [ ! -d "${rootfsDir}/${dir}" ]; then
          printf "%b" "missing\t\t"
	  printf "%b" "${rootfsDir}/${dir}\n"
          result=1
    elif [ "$(ls -lLd "${rootfsDir}/${dir}" | grep '^d.......w. ')" ]; then
          printf "%b" "world writable\t"
	  printf "%b" "${rootfsDir}/${dir}\n"
          result=1
    fi
   done

   echo $result
}

resRoot=$(check_path "$(echo "${rootPath}" | sed 's/PATH=\///g')")
resHome=$(check_path "$(echo "${homePath}" | sed 's/PATH=\///g')")

if [ "${resRoot}" != "0" ]; then
      echo "there are problematitic directories in the PATH variable in ${resRoot}"
      echo "${resRoot}"
      rc=1
elif [ "${resHome}" != "0" ]; then
      echo "there are problematitic directories in the PATH variable in ${resHome}"
      echo "${resHome}"
      rc=1
else
      echo "the directories in the path are fine"
fi

exit $rc
