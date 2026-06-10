import pytest

"""
Ref: SRG-OS-000780-GPOS-00240

Verify the operating system is configured to provide protected storage for
cryptographic keys with organization-defined safeguards and/or hardware
protected key store.
"""


@pytest.mark.feature("_tpm")
def test_tpm2_service_enabled(systemd):
    assert systemd.is_enabled("tpm2")
    assert systemd.is_active("tpm2")
