#!/usr/bin/env bash

set -u

DETAILS_FILE="$(mktemp /tmp/dmesg_details_XXXX.log)"

append_section_plain() {
  local level="$1" tag="$2"
  {
    echo "===== $tag ====="
    dmesg -k --color=never --level="$level" -T
    echo
  } >> "$DETAILS_FILE"
}

append_section_plain emerg  "EMERG"
append_section_plain alert  "ALERT"
append_section_plain crit   "CRIT"
append_section_plain err    "ERROR"
append_section_plain warn   "WARN"
append_section_plain notice "NOTICE"
append_section_plain info   "INFO"
append_section_plain debug  "DEBUG"

critical_count="$(dmesg -k --level=emerg,alert,crit,err | wc -l | awk '{print $1}')"
warn_count="$(dmesg -k --level=warn | wc -l | awk '{print $1}')"

echo "ATTACHMENT: $DETAILS_FILE"

echo "==== dmesg Summary ===="
echo "Critical errors: $critical_count"
echo "Warnings:        $warn_count"

if [ "$critical_count" -gt 0 ]; then
  echo -e "RESULT: FAIL — Critical errors detected in dmesg"
  exit 1
else
  echo -e "RESULT: PASS — No critical errors found in dmesg"
  exit 0
fi
