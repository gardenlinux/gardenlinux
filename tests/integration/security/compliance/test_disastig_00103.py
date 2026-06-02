import pytest

"""
Ref: SRG-OS-000269-GPOS-00103

Verify, in the event of a system failure, the operating system preserves any
information necessary to determine cause of failure and any information
necessary to return to operations with least disruption to mission processes.
"""


def test_disastig_00103():
    pytest.skip(
        reason="covered by core/test_services::test__kdump_kdump_tools_service_enabled, integration/boot/test_initrd::test_kdump_initrd_files"
    )
