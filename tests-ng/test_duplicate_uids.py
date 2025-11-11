from typing import Dict, List

from plugins.password_shadow import passwd_entries
from plugins.utils import check_for_duplicates


def test_duplicate_uids(passwd_entries: List[Dict[str, str | List[str]]]):
    """
    Check if any duplicate userids are defined in /etc/passwd.
    """
    duplicates = check_for_duplicates(entries=passwd_entries, field="uid")
    assert (
        len(duplicates) == 0
    ), f"uids {duplicates} are used multiple times in /etc/passwd"


def test_duplicate_uids_detection(passwd_entries: List[Dict[str, str | List[str]]]):
    """
    Appending an existing entry to the list to check if the duplication check finds this.
    """
    passwd_entries.append(passwd_entries[0])

    duplicates = check_for_duplicates(entries=passwd_entries, field="uid")
    assert len(duplicates) == 1, f"duplicate uid is not found successfully"
    assert duplicates[0] == passwd_entries[0]["uid"]
