#!/bin/bash

if grep -q "clocksource=" /proc/cmdline; then
        exit 0
fi

hypervisor=$(systemd-detect-virt)
available_clock_sources=$(cat /sys/devices/system/clocksource/clocksource0/available_clocksource)
case $hypervisor in
kvm|amazon)
 if [[ "$available_clock_sources" =~ "kvm-clock" ]] ; then
   echo "Detected hypervisor KVM/Amazon Nitro, setting clocksource kvm-clock" | systemd-cat -p info -t clocksource-setup
   echo kvm-clock > /sys/devices/system/clocksource/clocksource0/current_clocksource
 fi
 ;;
xen)
 if [[ "$available_clock_sources" =~ "tsc" ]] ; then
   echo "Detected hypervisor XEN, setting clocksource tsc" | systemd-cat -p info -t clocksource-setup
   echo tsc > /sys/devices/system/clocksource/clocksource0/current_clocksource
 fi
 ;;
esac

