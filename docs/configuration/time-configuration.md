---
title: Time configuration
weight: 10
disableToc: false
---

This document describes the time configuration (NTP, PTP, etc.) in Garden Linux images.

# Time (NTP) configuration in Garden Linux

Depending on the cloud provider for which the Garden Linux is built, different time sources are configured. The configuration generally follows the recommendations of the cloud providers.

If not mentioned otherwise, Garden Linux used [_systemd-timesyncd_](https://www.freedesktop.org/software/systemd/man/systemd-timesyncd.service.html) for time synchronization.

## AWS

For AWS, NTP is used and configured to retrieve the time from Amazons NTP server at `169.254.169.123`.

The time source is configured in [`features/aws/file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-aws.conf`](../../features/aws/file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-aws.conf).

Also refer to [Amazons documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html).

## GCP

For GCP, NTP is used and configured to retrieve the time from Googles NTP server at `metadata.google.internal`.

The time source is configured in [`features/gcp/file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-gcp.conf`](../../features/gcp/file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-gcp.conf).

Also refer to [Googles documentation](https://cloud.google.com/compute/docs/instances/configure-ntp).

## Azure

For Azure, [PTP](https://en.wikipedia.org/wiki/Precision_Time_Protocol) is used instead of NTP. For that, Garden Linux uses [_chrony_](https://chrony-project.org/)
as _systemd-timesyncd_ does not support PTP.

The time is configured in [`features/azure/file.include/etc/chrony/chrony.conf`](../../features/azure/file.include/etc/chrony/chrony.conf).

Also refer to [Microsofts documentation](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/time-sync).

## Alibaba Cloud

For AliCloud, NTP is used and configured to retrieve the time from AliClouds NTP servers at different addresses.

The time source is configured in [`features/ali/file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-ali.conf`](../../features/ali/file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-ali.conf).

Also refer to [Alibaba Clouds documentation](https://www.alibabacloud.com/help/en/ecs/user-guide/alibaba-cloud-ntp-server).

## OpenStack

For OpenStack, NTP is generally used. Since individual OpenStack landscapes can be vastly different, the NTP configuration has to come in through cloud-init.
