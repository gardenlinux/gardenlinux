import pytest

"""
Ref: SRG-OS-000206-GPOS-00084

Verify the operating system reveals error messages only to authorized users.
"""


@pytest.mark.feature("disaSTIGmedium")
def test_systemd_journal_is_not_world_readable(file):
    assert file.is_owned_by_user("/var/log/journal", "root")
    assert file.has_permissions("/var/log/journal", "rwxr-s---")
