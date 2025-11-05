from pathlib import Path
from typing import Dict, List

import pytest

from .utils import parse_etc_file


@pytest.fixture
def passwd_entries() -> List[Dict[str, str | List[str]]]:
    """
    Return parsed entries from /etc/passwd.
    Fields: user, passwd, uid, gid
    """
    path = Path("/etc/passwd")
    return parse_etc_file(
        path, field_names=["user", "passwd", "uid", "gid"], min_fields=4
    )


@pytest.fixture
def shadow_entries() -> List[Dict[str, str | List[str]]]:
    """
    Return parsed entries from /etc/shadow.
    Fields: user, passwd
    """
    path = Path("/etc/shadow")
    return parse_etc_file(path, field_names=["user", "passwd"], min_fields=2)


@pytest.fixture
def group_entries() -> List[Dict[str, str | List[str]]]:
    """
    Return parsed entries from /etc/group.
    Fields: group_name, password, gid, user_list
    """
    path = Path("/etc/group")
    return parse_etc_file(
        path, field_names=["group_name", "password", "gid", "user_list"], min_fields=4
    )
