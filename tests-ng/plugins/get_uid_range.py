import pytest
from dataclasses import dataclass
from pathlib import Path

@dataclass
class UIDRange:
    uid_min: int = None
    uid_max: int = None

@pytest.fixture
def get_uid_range() -> UIDRange:
    uid_range = UIDRange()
    output = Path("/etc/login.defs").read_text().strip()
    for line in output.split("\n"):
        if not line or line.startswith("#"):
            continue
        if line.startswith("UID_MIN"):
            uid_range.uid_min = int(line.split()[1])
        elif line.startswith("UID_MAX"):
            uid_range.uid_max = int(line.split()[1])
    return uid_range
