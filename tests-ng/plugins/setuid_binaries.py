import os
import pathlib

import pytest


@pytest.fixture
def exposed_setuid_binaries():
    """
    Returns a set of pathnames of root-owned binaries with setuid bit which are
    also "others"-executable (i.e. binaries that give root privileges to every
    user).
    """
    dirs = [
        "/usr/sbin",
        "/usr/bin",
        "/usr/libexec",
        "/usr/local/sbin",
        "/usr/local/bin",
    ]
    return {
        str(p)
        for d in dirs
        for root, _, files in os.walk(d)
        for p in map(lambda n: pathlib.Path(root) / n, files)
        if p.stat().st_uid == 0  # file belongs to root
        and (m := p.stat().st_mode) & 0o4000  # set‑uid bit present
        and ((m >> 3) & 0o111)  # “others” execute bit set
    }
