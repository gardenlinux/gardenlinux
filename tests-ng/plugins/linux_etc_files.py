from dataclasses import dataclass, field
from typing import List

import pytest


@dataclass
class Shadow:
    """
    Entry from /etc/shadow
    """

    login_name: str = field(compare=True)
    encrypted_password: str
    date_of_last_password_change: str
    minimum_password_age: str
    maximum_password_age: str
    password_warning_period: str
    password_inactivity_period: str
    account_expiration_date: str = field(default="")
    reserved_field: str = field(default="")


@dataclass
class Passwd:
    """
    Entry from /etc/passwd
    """

    name: str
    password: str
    uid: str = field(compare=True)
    gid: str
    gecos: str
    home_directory: str
    shell: str


@dataclass
class Group:
    """
    Entry from /etc/group
    """

    groupname: str
    password: str
    gid: str = field(compare=True)
    user_list: List[str]


@pytest.fixture
def passwd_entries() -> List[Passwd]:
    """
    Return parsed entries from /etc/passwd.
    """
    result = list[Passwd]()

    with open(file="/etc/passwd", encoding="utf-8") as f:
        for line in f.readlines():
            if not line.strip() or line.startswith("#"):
                continue  # Skip comments and empty lines
            fields = line.split(sep=":")
            if len(fields) != 7:
                raise ValueError(
                    f"/etc/passwd-entry has {len(fields)} instead of expected 7 fields."
                )

            result.append(Passwd(*fields))

    return result


@pytest.fixture
def shadow_entries() -> List[Shadow]:
    """
    Return parsed entries from /etc/shadow.
    """
    result = list[Shadow]()

    with open(file="/etc/shadow", encoding="utf-8") as f:
        for line in f.readlines():
            if not line.strip() or line.startswith("#"):
                continue  # Skip comments and empty lines
            fields = line.split(sep=":")
            if len(fields) != 9:
                raise ValueError(
                    f"/etc/shadow-entry has {len(fields)} instead of expected 9 fields."
                )

            result.append(Shadow(*fields))

    return result


@pytest.fixture
def group_entries() -> List[Group]:
    """
    Return parsed entries from /etc/group.
    """
    result = list[Group]()

    with open(file="/etc/group", encoding="utf-8") as f:
        for line in f.readlines():
            if not line.strip() or line.startswith("#"):
                continue  # Skip comments and empty lines
            fields = line.split(sep=":")
            if len(fields) != 4:
                raise ValueError(
                    f"/etc/group-entry has {len(fields)} instead of expected 4 fields."
                )

            result.append(
                Group(
                    groupname=fields[0],
                    password=fields[1],
                    gid=fields[2],
                    user_list=fields[3].split(","),
                )
            )

    return result
