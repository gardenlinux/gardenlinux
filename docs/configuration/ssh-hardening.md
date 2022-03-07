---
title: SSH Hardening
weight: 10
disableToc: false
---

This document highlights which SSH configuration parameters are set in Garden Linux in order to harden it. Thereby, it also explains why specific values have been set and what were the reasons for them.

## Configuration parameters
The SSH configuration of Garden Linux is mainly done in the [server feature](https://github.com/gardenlinux/gardenlinux/tree/main/features/server).

It provides the `openssh-server` package and the corresponding configuration ([sshd_config]((https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/ssh/sshd_config))) to properly install and configure a SSH server.

By that, the following aspects has been taken into consideration to improve the overall security.

### Direct Root Login
Direct root login **MUST** be disabled. Therefore, the `PermitRootLogin` parameter is set to `no`.

### TCP Forwarding
Disabling the TCP Forwarding does not bring a significant security improvement since users which have SSH access to hosts are still able to use other forwarders like `nc` or `socat` to work around this limitation.

Moreover, there are cases in which this feature is explicitly required. This is the case for the Gardener bastion host for example.

As a result, TCP Forwarding is not disabled in Garden Linux.

### X11 Forwarding
X11 Forwarding on the other hand is already disabled by default in the OpenSSH configuration.

However, the corresponding `sshd_config` of Garden Linux explicitly sets the `X11Forwarding` parameter to `no`

### Public Key Authentication
Public Key Authentication is the preferred authentication method in Garden Linux. There may also be some cloud providers which are enabling password authentication by default, but Garden Linux only enables Public Key Authentication

This is achieved by setting the `AuthenticationMethods` parameter to `publickey` only.

### Verbose Log Level
In order to provide a good audit track, a verbose Log Level of SSH is recommended.

For this reason, Garden Linux sets the `LogLevel` parameter to `VERBOSE` to achieve this.

### Host authentication
In general, host authentication should not be enabled by default. Only automated processes **MAY** use this authentication method.

By default, Garden Linux sets the `HostbasedAuthentication` parameter to `no` to disable host authentication.

### Cipher Suites, Kex Algorithms and Message Authentication Codes
Overall, the default Cipher Suites of OpenSSH - as they are used in Garden Linux via the `debian/testing` package - already fulfill a specific level of security.

The designated SSH Team of Debian always tries to use a State of the Art level of security for the Cipher Suites, Kex Algorithms and MACs.

#### Cipher Suites

The [OpenSSH configuration](https://salsa.debian.org/ssh-team/openssh/-/blob/debian/1%258.8p1-1/sshd_config.0#L276-278) uses the following ciphers:
```
chacha20-poly1305@openssh.com,
aes128-ctr,aes192-ctr,aes256-ctr,
aes128-gcm@openssh.com,aes256-gcm@openssh.com
```

As [RFC 9142](https://datatracker.ietf.org/doc/rfc9142/) stats, the default ciphers used by OpenSSH are considered to be strong.

#### Kex Algorithms

The [OpenSSH configuration](https://salsa.debian.org/ssh-team/openssh/-/blob/debian/1%258.8p1-1/sshd_config.0#L582-586) uses Key Exchange (Kex) Algorithms like:
```
curve25519-sha256,curve25519-sha256@libssh.org,
ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,
diffie-hellman-group-exchange-sha256,
diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,
diffie-hellman-group14-sha256

```

As [RFC 9142](https://datatracker.ietf.org/doc/rfc9142/) stats, the default Kex Algorithms used by OpenSSH are considered to be strong, too.

#### Message Authentication Codes (MACs)

The [OpenSSH configuration](https://salsa.debian.org/ssh-team/openssh/-/blob/debian/1%258.8p1-1/sshd_config.0#L669-673) uses MACs like:
```
umac-64-etm@openssh.com,umac-128-etm@openssh.com,
hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,
hmac-sha1-etm@openssh.com,
umac-64@openssh.com,umac-128@openssh.com,
hmac-sha2-256,hmac-sha2-512,hmac-sha1
```

The OpenSSH default configuration still supports HMAC-SHA-1. Althrough SHA-1 is not recommended to be used as a plain hash algorithm, it can still be used as a hash algorithm for MACs as [RFC 6194](https://datatracker.ietf.org/doc/rfc6194/) stats:
```
As of today, there is no indication that attacks on SHA-1 can be extended to HMAC-SHA-1.
```
