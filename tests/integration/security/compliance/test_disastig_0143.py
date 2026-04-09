import pytest

"""
Ref: SRG-OS-000355-GPOS-00143

Verify the operating system, for networked systems, compares internal
information system clocks at least every 24 hours with an authoritative time
source.

Ref: SRG-OS-000356-GPOS-00144

Verify the operating system synchronizes internal information system clocks to
the authoritative time source when the time difference is greater than one
second.
"""


@pytest.mark.booted(reason="requires running systemd")
def test_time_sync_is_enabled(systemd):
    assert systemd.is_enabled("cronyd")


def test_time_is_synced_at_least_every_24_hours():
    pass
