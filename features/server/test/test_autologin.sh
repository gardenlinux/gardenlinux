#!/usr/bin/env bash

rootfsDir=$1
rc=0

# there should not be autologin.conf files under the /etc/systemd/ directory
echo "checking for autologin.conf files"
autologinFileName="autologin.conf"
systemdDir="${rootfsDir}/etc/systemd"
output=$(find "${systemdDir}" -name "${autologinFileName}")
numOfAutologinFiles=$(echo "${output}" | wc -l)

if [ -z "${output}" ]
then
      echo "There are no ${autologinFileName} files under ${systemdDir} directory"
else
      echo "${numOfAutologinFiles} ${autologinFileName} exist under ${systemdDir} directory:"
      echo "${output}"
      rc=1
fi

exit $rc
