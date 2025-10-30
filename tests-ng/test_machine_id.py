from pathlib import Path


def test_machine_id_file_exists():
    assert Path("/etc/machine-id").exists()


def test_machine_id_is_initialized():
    assert Path("/etc/machine-id").read_text() != ""
    assert Path("/etc/machine-id").read_text() != "uninitialized"
