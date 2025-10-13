import pytest
import tempfile

from .shell import ShellRunner


@pytest.fixture
def remounted_root(shell: ShellRunner):
    """
    Bind mounts the root path to a temporary directory and returns the temporary path. After text execution
    the bind mount is umounted and the temporary directory cleaned up automatically.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        shell(f"mount --bind / {tempdir}")
        yield tempdir
        shell(f"umount {tempdir}")
