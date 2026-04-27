import pytest
from plugins.linux_etc_files import Passwd


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.root(reason="requires access to /etc/passwd")
def test_no_duplicate_uids_in_passwd(passwd_entries: list[Passwd]):
    """
    As per DISA STIG compliance requirements, all accounts assigned to
    interactive users must be given unique User IDs (UIDs).
    This test verifies that no two entries in /etc/passwd share the same UID.
    Ref: SRG-OS-000104-GPOS-00051
    """
    seen = {}
    duplicates = []

    for entry in passwd_entries:
        if entry.uid in seen:
            duplicates.append(
                f"{entry.name} (uid={entry.uid}) duplicates {seen[entry.uid]}"
            )
        else:
            seen[entry.uid] = entry.name

    assert not duplicates, (
        "stigcompliance: duplicate UIDs found in /etc/passwd:\n"
        + "\n".join(duplicates)
    )
