#!/usr/bin/env bash 

set -eu

# set the default to iptalbes and deactivate nf_tables kernel modules
#
update-alternatives --set iptables /usr/sbin/iptables-legacy
update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy
update-alternatives --set arptables /usr/sbin/arptables-legacy
update-alternatives --set ebtables /usr/sbin/ebtables-legacy

# just to make sure there are no traces left
#
systemctl mask nftables.service
