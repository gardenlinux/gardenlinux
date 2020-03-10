#!/bin/bash
set -e

FEATURES="uefi docker frr iso"

IFS=' ' read -a feats <<< "${FEATURES}"


cd build-steps
for s in `find * -type d`
do
    curfeat=`echo $s | cut -d- -f2`
    for f in "${feats[@]}"
    do
        if [ "$curfeat" = "$f" ]; then
            echo ""
            echo "--------------------------------------------------------------------"
            echo " GARDENLINUX BUILD-STEP: $s"
            echo "--------------------------------------------------------------------"
            echo ""
            $s/build.sh
        fi
    done
done