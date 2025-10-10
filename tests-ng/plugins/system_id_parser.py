import pytest
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class UIDRange:
    uid_min: int = None
    uid_max: int = None
    uid_range: range = field(init=False)

    def __post_init__(self):
        assert self.uid_min is not None, "UID_MIN not found"
        assert self.uid_max is not None, "UID_MAX not found"
        assert self.uid_max > self.uid_min, "UID_MAX must be greater than UID_MIN"

        self.uid_range = range(self.uid_min, self.uid_max + 1)

    def __contains__(self, uid: int) -> bool:
        return uid in self.uid_range

def parse_config():
    config = {}
    login_defs_path=Path("/etc/login.defs")
    assert login_defs_path.exists(), f"{login_defs_path} doesn't exist"
    for line in login_defs_path.read_text().splitlines():
        line = line.strip()
        # Skip blank lines and comments
        if not line or line.startswith('#'):
            continue
        config_line = line.split(None, 1)
        if len(config_line) == 2:
            key, value = config_line
            config[key] = value
    return config

@pytest.fixture
def regular_user_uid_range() -> UIDRange:
    uid_min = int(parse_config()["UID_MIN"])
    uid_max = int(parse_config()["UID_MAX"])

    uid_val = UIDRange(uid_min=uid_min, uid_max=uid_max)

    return uid_val
