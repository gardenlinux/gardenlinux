from typing import List

from plugins.linux_etc_files import Passwd
from plugins.utils import check_for_duplicates


def test_duplicate_uids(passwd_entries: List[Passwd]):
    """
    Check if any duplicate userids are defined in /etc/passwd.
    """
    duplicates = check_for_duplicates(entries=passwd_entries)
    assert (
        len(duplicates) == 0
    ), "uids {} are used multiple times in /etc/passwd".format(duplicates)


def test_duplicate_uids_detection(passwd_entries: List[Passwd]):
    """
    Appending an existing entry to the list to check if the duplication check finds this.
    """
    expected_duplicate = passwd_entries[0]
    passwd_entries.append(expected_duplicate)

    duplicates = check_for_duplicates(entries=passwd_entries)
    assert len(duplicates) == 1, "duplicate entry is not found successfully"
    assert expected_duplicate == duplicates[0]
