from typing import List

import pytest
from plugins.linux_etc_files import Group, group_entries
from plugins.utils import check_for_duplicates


@pytest.fixture(scope="function")
def group(group_entries: List[Group], request: pytest.FixtureRequest):
    """
    Extract the group from the system group list.
    """
    group_name = request.param if hasattr(request, "param") else None
    group_list = [group for group in group_entries if group.groupname == group_name]
    group = group_list[0] if group_list else None

    assert group, f"Group {group_name} is not present."
    return group


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
    Check if duplication check works by adding a duplicate.
    """
    duplicate_group = group_entries[0]
    group_entries.append(duplicate_group)

    duplicates = check_for_duplicates(group_entries)
    assert (
        len(duplicates) == 1
    ), f"Group #{duplicate_group.groupname} should be found as duplicate, but was not."


@pytest.mark.parametrize("group, user_list", [("root", [])], indirect=["group"])
@pytest.mark.feature("not _dev and not pythonDev")
def test_group_root_has_no_users(
    group_entries: List[Group], group: Group, user_list: List[str]
):
    """
    Check if parameterized groups have the expected users.
    """
    assert (
        group.user_list == user_list
    ), f"assigned users from group {group.groupname} dont match expected {user_list}. Was: {group.user_list}"


@pytest.mark.parametrize("group, user_list", [("wheel", [])], indirect=["group"])
@pytest.mark.feature("not _dev and not pythonDev and not container")
def test_group_wheel_has_no_users(
    group_entries: List[Group], group: Group, user_list: List[str]
):
    """
    Check if parameterized groups have the expected users.
    """
    assert (
        group.user_list == user_list
    ), f"assigned users from group {group.groupname} dont match expected {user_list}. Was: {group.user_list}"
