#!/usr/bin/env bash

sed -i 's/Provisioning.RegenerateSshHostKeyPair=y/Provisioning.RegenerateSshHostKeyPair=n/g;s/Provisioning.DecodeCustomData=n/Provisioning.DecodeCustomData=y/g;s/OS.EnableFirewall=n/OS.EnableFirewall=y/g;s/Provisioning.ExecuteCustomData=n/Provisioning.ExecuteCustomData=y/g' /etc/waagent.conf 
