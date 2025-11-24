# 24. FIPSification of Garden Linux

Date: 2025-11-24

## Status

Draft

## Context

In this ADR, we’re going to discuss how to make the FIPS feature available for the public. Currently
it’s possible to use the FIPS feature and join a Gardener cluster with that very image. However,
this is a manual effort, but essentially the features are working.

A key concern is the way we make FIPS usable for users. By now, we would provide a static image that
has all the necessary configurations set and will work out-of-the-box. Switching to Garden Linux
might come with some handicap, since it might imply that software will not work.


    Err:1 https://packages.gardenlinux.io/gardenlinux today/main arm64 grep arm64 3.12-1
      OpenSSL error: error:0308010C:digital envelope routines::unsupported  Error reading from server - read (5: Input/output error) [IP: X.Y.Z.X 443]

Here is an error message as an example of where the FIPS interface is with software. FIPS might be
hindering the portage of software to Garden Linux when the FIPS is enforced. Users need to test
their changes on a FIPS-enabled system but might want to disable FIPS to ensure that introduced
changes are working. Also, check how big the performance penalty is when testing software. This
should be done, in the best case, on the very same hardware. An 
option that is not possible with the current design.

Other Linux vendors provide tools like `fips-mode-setup` to set the respective configuration and
allow the system to be elevated to its FIPS configuration.


    # fips-mode-setup --enable
    Kernel initramdisks are being regenerated. This might take some time.
    Setting system policy to FIPS
    Note: System-wide crypto policies are applied on application start-up.
    It is recommended to restart the system for the change of policies
    to fully take place.
    FIPS mode will be enabled.
    Please reboot the system for the setting to take effect.


In this example from Red Hat, we can see that this will change all configuration files and deem a
reboot. Canonical has a tool that is OSS:
[`crypto-policies`](https://manpages.debian.org/unstable/crypto-policies/crypto-policies.7.en.html).
This tool was developed originally in Python, but the tool hasn’t been updated since 2019.

Also, this might work for a system with a legacy configuration, but it would not be suited for the
usage within a UCI like Trustedboot requires. This implies that we have to configure each system
with two UCI images, the default one and the version with FIPS enabled. Next would be to have the
power to  provide different configurations to our system, based on the boot UCI. In theory this
should be possible, considering that it would behave similarly to the in-place update feature.

Since many of the configurations and files necessary to put the system in FIPS mode reside on the
`/usr` partion, the usage of `systemd-sysext` might be suited for this pursuit.

When the decision is set against the elevation of a Garden Linux installation, it would lead to the
situation that Garden Linux would be locked into the delivery FIPS as its own product. The issue
motivating this decision and any context that influences or constrains the decision.


## Decision

The change that we're proposing or have agreed to implement.

## Consequences

What becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated.
