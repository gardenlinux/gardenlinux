from typing import List, Set

import pytest
from plugins.linux_etc_files import Group
from plugins.utils import check_for_duplicates


def test_groups_are_unique(group_entries: List[Group]):
    """
    Check if there are any duplicate groups in /etc/group.
    """
    duplicates = check_for_duplicates(group_entries)
    assert (
        len(duplicates) == 0
    ), f"Groups from /etc/group should not have duplicates: {duplicates}"


def test_groups_find_duplicate(group_entries: List[Group]):
    """
    Check if duplication check works by adding a duplicate.
    """
    duplicate_group = group_entries[0]
    group_entries.append(duplicate_group)

    duplicates = check_for_duplicates(group_entries)
    assert (
        len(duplicates) == 1
    ), f"Group #{duplicate_group.groupname} should be found as duplicate, but was not."


@pytest.mark.feature("not _dev and not pythonDev")
def test_group_root_has_no_users(group_entries: List[Group]):
    """
    Check if parameterized groups have the expected users.
    """
    group_list = [group for group in group_entries if group.groupname == "root"]
    group = group_list[0] if group_list else None

    assert group, "Group root is not present."

    assert (
        len(group.user_list) == 0
    ), f"user group root is not empty as expected. Was: {group.user_list}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-server-config-group-wheel",
    ]
)
@pytest.mark.feature("not _dev and not pythonDev and not container")
def test_group_wheel_has_no_unexpected_users(
    group_entries: List[Group], expected_users: Set[str]
):
    """
    Check if parameterized groups have the expected users.
    """
    group_list = [group for group in group_entries if group.groupname == "wheel"]
    group = group_list[0] if group_list else None

    assert group, "Group wheel is not present."

    # remove expected users from group as we want to check for unexpected users
    expected_user_list = [
        user for user in group.user_list if user not in expected_users
    ]

    assert (
        len(expected_user_list) == 0
    ), f"user group wheel is not empty as expected. Was: {expected_user_list}"
