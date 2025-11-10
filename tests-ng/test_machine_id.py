from pathlib import Path

import pytest


@pytest.mark.booted(reason="sysctl needs a booted system")
def test_machine_id_file_exists():
    assert Path("/etc/machine-id").exists()


@pytest.mark.booted(reason="sysctl needs a booted system")
def test_machine_id_is_initialized():
    assert Path("/etc/machine-id").read_text() != ""
    assert Path("/etc/machine-id").read_text() != "uninitialized"
