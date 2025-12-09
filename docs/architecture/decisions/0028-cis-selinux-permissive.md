# 28. Build features/cis with SELINUX=permissive Instead of SELINUX=enforcing

Date: 2025-12-13

## Status: 

Accepted

## Context

In the Garden Linux CIS hardening effort, the features/cis image was supposed to be aligned with a strict security with SELINUX=enforcing

However, during testing and platform integration, several practical issues were identified when running CIS-hardened images with SELinux in enforcing mode, with lots of services at startup breaking, which needs a long investment for fixing.

 - Service startup failures due to missing or incompatible SELinux policies for:

   - auditd
   - sshd
   - provisioning services (e.g., Ignition-related units)


During the alignment meeting on Oct 23 and followup on Oct 29, the CIS with SELINUX=enforcing in parallel container startup was reviewed for the CIS feature set which failed to boot. Accordingly, it was decided with Andre Russ, Thomas Mangold, Stefan Catargiu, Pavel Pavlov that for now it would be acceptable to work on features/cis with SELINUX=permissive.


## Decision

 The features/cis image will be built with:
```bash
SELINUX=permissive
```

instead of:
```bash
SELINUX=enforcing
```

This ensures that:

 - SELinux remains enabled and auditable

 - Policy violations are still logged

 - System behavior is not blocked at runtime and we proceed for CIS compliance requirements for now

This decision applies specifically to only:

`features/cis`

CIS-hardened immutable Garden Linux images

It does not change the default SELinux behavior for non-CIS or non-immutable variants.

## Consequences

 - System stability: Prevents boot and service failures caused by missing/incomplete SELinux policies.

 - Operational safety: Avoids lockouts and emergency states on immutable images.

 - Audit visibility preserved: AVC denials are still logged and observable.


## Final Outcome

The team formally agreed to proceed with:

```bash
SELINUX=permissive
```

for `features/cis`, as the balance between security, reliability, and maintainability for current Garden Linux CIS images.
