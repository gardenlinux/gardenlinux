#!/bin/bash

set -Eeuo pipefail

NETFILTER_GARDENER="/var/lib/gardener-gardenlinux/etc/netfilter_frontend"

function check_netfilter_frontend {
    # taken from Kubernetes
    # https://github.com/kubernetes/kubernetes/blob/623b6978866b5d3790d17ff13601ef9e7e4f4bf0/build/debian-iptables/iptables-wrapper#L28-L38
    num_legacy_lines=$( (iptables-legacy-save || true; ip6tables-legacy-save || true) 2>/dev/null | grep '^-' | wc -l)
    if [ "${num_legacy_lines}" -ge 10 ]; then
        mode=legacy
    else
        num_nft_lines=$( (timeout 5 sh -c "iptables-nft-save; ip6tables-nft-save" || true) 2>/dev/null | grep '^-' | wc -l)
        if [ "${num_legacy_lines}" -ge "${num_nft_lines}" ]; then
            mode=legacy
        else
            mode=nft
        fi
    fi
    echo $mode
}

# no need to run if Gardener did not place a configuration for netfilter backend
[ ! -f "$NETFILTER_GARDENER" ] && exit 0

desired_nff=$(cat "$NETFILTER_GARDENER")
current_nff=$(check_netfilter_frontend)

if [ "$desired_nff" == "iptables" -o "$desired_nff" == "legacy" ]; then
    nf_frontend="/usr/sbin/iptables-legacy"
    nf6_frontend="/usr/sbin/ip6tables-legacy"
elif [ "$desired_nff" == "nftables" -o "$desired_nff" == "nft" ]; then
    nf_frontend="/usr/sbin/iptables-nft"
    nf6_frontend="/usr/sbin/ip6tables-nft"
fi

for nff in $nf_frontend $nf_frontend; do
    if [ ! -x "$nff" ]; then
        echo "$nff does not exist or is not executable" >&2
        exit 1
    fi
done

update-alternatives --set iptables "$nf_frontend" > /dev/null
update-alternatives --set ip6tables "$nf6_frontend" > /dev/null
