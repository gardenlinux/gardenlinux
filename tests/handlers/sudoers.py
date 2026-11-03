import shutil
from pathlib import Path

import pytest

SUDOERS_PATH = Path("/etc/sudoers")
SUDOERS_BACKUP = Path("/etc/sudoers.bak")


def handle_sudoers_edit():
    """Remove the '# Host alias specification' line from /etc/sudoers, then restore."""
    original = SUDOERS_PATH.read_text()
    shutil.copy2(SUDOERS_PATH, SUDOERS_BACKUP)

    filtered = "".join(
        line
        for line in original.splitlines(keepends=True)
        if not line.startswith("# Host alias specification")
    )
    SUDOERS_PATH.write_text(filtered)

    yield

    shutil.copy2(SUDOERS_BACKUP, SUDOERS_PATH)
    SUDOERS_BACKUP.unlink()


@pytest.fixture
def sudoers_edit():
    """Handler: remove '# Host alias specification' from /etc/sudoers; restore on teardown."""
    yield from handle_sudoers_edit()
