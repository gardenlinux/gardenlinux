#!/usr/bin/env bash

sed -i 's/Provisioning.RegenerateSshHostKeyPair=y/Provisioning.RegenerateSshHostKeyPair=n/g;s/Provisioning.DecodeCustomData=n/Provisioning.DecodeCustomData=y/g;s/OS.EnableFirewall=n/OS.EnableFirewall=y/g;s/Provisioning.UseCloudInit=n/Provisioning.UseCloudInit=y/g' /etc/waagent.conf 
