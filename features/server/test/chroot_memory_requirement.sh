#!/usr/bin/env bash

rootfsDir=$1
rc=0

# check memory protection
echo "check memory protection"
sysctlBin="${rootfsDir}/sbin/sysctl"
expectedKey="^kernel.randomize_va_space"
expectedValue="2"
output=$("${sysctlBin}" -a | grep "${expectedKey} = ${expectedValue}")

if [ -z "${output}" ]
then
      echo "${expectedKey} shoult be set to ${expectedValue}"
      rc=1
else
      echo "configurations are correct"
fi

exit $rc
