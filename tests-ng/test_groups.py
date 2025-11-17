from typing import Dict, List

import pytest
from plugins.linux_etc_files import Group, group_entries
from plugins.utils import check_for_duplicates


def test_groups_are_unique(group_entries: List[Group]):
    """
    Check if there are any duplicates in /etc/group.
    """
    duplicates = check_for_duplicates(group_entries)
    assert (
        len(duplicates) == 0
    ), f"Groups from /etc/group should not have duplicates: {duplicates}"


def test_groups_find_duplicate(group_entries: List[Group]):
    """
    Check if there are any duplicates in /etc/group, by adding a duplicate.
    """
    duplicate_group = group_entries[0]
    group_entries.append(duplicate_group)

    duplicates = check_for_duplicates(group_entries)
    assert (
        len(duplicates) == 1
    ), f"Group #{duplicate_group.groupname} should be found as duplicate, but was not."


@pytest.mark.parametrize("group_name", ["root", "wheel"])
@pytest.mark.feature("not _dev and not pythonDev")
def test_groups_are_present(group_entries: List[Group], group_name: str):
    assert any(
        group_entry.groupname == group_name for group_entry in group_entries
    ), f"group {group_name} is not present."


@pytest.mark.parametrize("group_name,user_list", [("root", []), ("wheel", [])])
@pytest.mark.feature("not _dev and not pythonDev")
def test_groups_with_no_users(
    group_entries: List[Group], group_name: str, user_list: List[str]
):
    """
    Check if parameterized groups have the expected users.
    """
    group = [group for group in group_entries if group.groupname == group_name][0]

    assert (
        group.user_list == user_list
    ), f"assigned users from group {group.groupname} dont match expected {user_list}. Was: {group.user_list}"
