# SSH Hardening

This document highlights which SSH configuration parameters are set in Garden Linux in order to harden it. Thereby, it also explains which specific values are set and what their reasons are.

## Configuration parameters
The SSH configuration of Garden Linux is mainly done in the [server feature](https://github.com/gardenlinux/gardenlinux/tree/main/features/server).

It provides the `openssh-server` package and the corresponding configuration ([sshd_config](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/ssh/sshd_config)) to properly install and configure a SSH server.

By that, the following aspects has been taken into consideration to improve the overall security.

### Direct Root Login
Direct root login **MUST** be disabled. As a result, the `PermitRootLogin` parameter is set to `no`.

### TCP Forwarding
Disabling the TCP Forwarding does not bring a significant security improvement since users that have SSH access are still able to use other forwarders like `nc` or `socat` to work around this limitation.

Moreover, there are cases in which this feature is explicitly required. This is the case for the Gardener bastion host for example.

Therefore, TCP Forwarding is not disabled in Garden Linux.

### X11 Forwarding
Besides the TCP Forwarding, X11 Forwarding on the other hand is already disabled in the OpenSSH configuration by default.

In addition, the corresponding `sshd_config` of Garden Linux explicitly sets the `X11Forwarding` parameter to `no`

### Public Key Authentication
Public Key Authentication is the preferred authentication method in Garden Linux. There might be some cloud providers which are enabling password authentication for their customers after the initialization, but Garden Linux only enables Public Key Authentication by default.

This is achieved by setting the `AuthenticationMethods` parameter to `publickey` only.

### Verbose Log Level
In order to provide a good audit track, a verbose Log Level of the SSH Server is recommended.

For this reason, Garden Linux sets the `LogLevel` parameter to `VERBOSE`.

### Host authentication
In general, host authentication should not be enabled by default. Only automated processes **MAY** use this authentication method.

As a result, Garden Linux sets the `HostbasedAuthentication` parameter to `no` to disable host authentication.

### Cipher Suites, Kex Algorithms and Message Authentication Codes
Overall, the default Cipher Suites of OpenSSH already provides a set of algorithms that are considered to be safe. Thereby, Garden Linux uses the OpenSSH version that `debian/testing` provides, so there is an additional layer of trust.

If the default configuration of OpenSSH would provide a non secure Cipher Suite, Kex Algorithm or Message Authentication Code, this team would probably remove the corresponding algorithm from the default list.

#### Cipher Suites

The [OpenSSH configuration](https://salsa.debian.org/ssh-team/openssh/-/blob/debian/1%258.9p1-3/sshd_config.0#L276-278) of the corresponding Debian package uses the following default ciphers:
```
chacha20-poly1305@openssh.com,
aes128-ctr,aes192-ctr,aes256-ctr,
aes128-gcm@openssh.com,aes256-gcm@openssh.com
```

#### Kex Algorithms

The [OpenSSH configuration](https://salsa.debian.org/ssh-team/openssh/-/blob/debian/1%258.9p1-3/sshd_config.0#L580-585) of the corresponding Debian package uses default Key Exchange (Kex) Algorithms like:
```
curve25519-sha256,curve25519-sha256@libssh.org,
ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,
sntrup761x25519-sha512@openssh.com,
diffie-hellman-group-exchange-sha256,
diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,
diffie-hellman-group14-sha256

```

As [RFC 9142](https://datatracker.ietf.org/doc/rfc9142/) stats, the default Kex Algorithms used by OpenSSH are considered to be strong.

#### Message Authentication Codes (MACs)

The [OpenSSH configuration](https://salsa.debian.org/ssh-team/openssh/-/blob/debian/1%258.9p1-3/sshd_config.0#L668-672) of the corresponding Debian package uses default MACs like:
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
