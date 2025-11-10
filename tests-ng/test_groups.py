from typing import Dict, List

import pytest
from plugins.password_shadow import group_entries


@pytest.mark.parametrize("group_name,user_list", [("root", []), ("wheel", [])])
@pytest.mark.feature("not container")
def test_groups_with_no_users(
    group_entries: List[Dict[str, str | List[str]]], group_name, user_list
):
    """
    Check if parameterized groups have the expected users.
    """
    # find the parameterized group in the dataset
    matching_groups = [
        group_entry
        for group_entry in group_entries
        if group_entry["group_name"] == group_name
    ]
    assert (
        len(matching_groups) == 1
    ), f"No exact match found for group {group_name}. Found {len(matching_groups)}, expected only 1"

    # we have only group available
    grp = matching_groups[0]

    if isinstance(grp["user_list"], list):
        # list, should not happen here, as group_entries will split by : by default and not comma as expected
        actual_user_list = grp["user_list"]
    elif isinstance(grp["user_list"], str):
        # single entry or empty
        actual_user_list = grp["user_list"].strip().split(",")
    else:
        raise ValueError(f"user_list is of unhandled type")

    # python split on an empty array will return [''] instead of []
    actual_user_list = [a for a in actual_user_list if a.strip() != ""]

    assert (
        actual_user_list == user_list
    ), f"assigned users from group {grp["group_name"]} dont match expected {user_list}. Was: {actual_user_list}"
