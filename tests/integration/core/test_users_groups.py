import os
import pwd
from typing import List, Set

import pytest
from plugins.file import File
from plugins.linux_etc_files import Group, Passwd
from plugins.users import User
from plugins.utils import check_for_duplicates

# =============================================================================
# Misc settings not tied to any specific feature
# =============================================================================


def test_service_accounts_have_nologin_shell(regular_user_uid_range):
    for entry in pwd.getpwall():
        if entry.pw_uid in regular_user_uid_range:
            continue
        if entry.pw_name in {"root", "sync"}:
            continue
        assert entry.pw_shell in [
            "/usr/sbin/nologin",
            "/bin/false",
        ], f"User {entry.pw_name} has unexpected shell: {entry.pw_shell}"


def test_root_home_permissions(file: File):
    assert file.has_mode("/root", "0700"), "/root has incorrect permissions"


@pytest.mark.feature("not _dev")
def test_no_extra_home_directories(expected_users, file: File):
    if file.is_symlink("/home"):
        return
    entries = os.listdir("/home")
    unexpected = [e for e in entries if e not in expected_users]
    assert not unexpected, f"Unexpected entries in /home: {entries}"


@pytest.mark.testcov(["GL-TESTCOV-aws-config-cloud-user-sudo"])
@pytest.mark.booted
@pytest.mark.root(reason="Using sudo command to check the access")
def test_users_sudo_capability(get_all_users, expected_users, user: User):
    users_with_sudo_capabilities = set(
        [u for u in get_all_users if user.is_user_sudo(u)]
    )
    allowed_sudo_users = set(expected_users) | {"root", "dev"}
    unexpected_sudo_users = users_with_sudo_capabilities - allowed_sudo_users

    assert (
        not unexpected_sudo_users
    ), f"Unexpected sudo capability {unexpected_sudo_users}"


def test_available_regular_users(get_regular_users, expected_users):
    allowed_users = ["dev", "nobody"] + list(expected_users)
    unexpected_user = [user for user in get_regular_users if user not in allowed_users]

    assert (
        not unexpected_user
    ), f"Unexpected user account found in /etc/passwd, {unexpected_user}"


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
