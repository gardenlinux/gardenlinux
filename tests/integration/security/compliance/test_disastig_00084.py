"""
Ref: SRG-OS-000206-GPOS-00084

Verify the operating system reveals error messages only to authorized users.
"""

import pytest


@pytest.mark.security_id(203664)
@pytest.mark.feature("disaSTIGmedium")
def test_systemd_journal_is_not_world_readable(file):
    """Verify /var/log/journal is owned by root with mode rwxr-s---."""
    assert file.is_owned_by_user("/var/log/journal", "root")
    assert file.has_permissions("/var/log/journal", "rwxr-s---")
