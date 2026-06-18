"""
Ref: SRG-OS-000780-GPOS-00240

Verify the operating system is configured to provide protected storage for
cryptographic keys with organization-defined safeguards and/or hardware
protected key store.
"""

import pytest


@pytest.mark.security_id(263660)
@pytest.mark.feature("_tpm")
def test_tpm2_service_enabled(systemd):
    """Verify the tpm2 service is enabled and active."""
    assert systemd.is_enabled("tpm2")
    assert systemd.is_active("tpm2")
