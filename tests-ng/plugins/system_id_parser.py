import pytest
from dataclasses import dataclass
from pathlib import Path


@dataclass
class UIDRange:
    uid_min: int = None
    uid_max: int = None

    def __post_init__(self):
        assert self.uid_min is not None, "UID_MIN not found"
        assert self.uid_max is not None, "UID_MAX not found"
        assert self.uid_max > self.uid_min, "UID_MAX must be greater than UID_MIN"

    def __contains__(self, uid: int) -> bool:
        return self.uid_min <= uid <= self.uid_max

def parse_config(path):
    config = {}
    login_defs_path=Path(path)
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
    config_path = "/etc/login.defs"
    uid_min = int(parse_config(config_path)["UID_MIN"])
    uid_max = int(parse_config(config_path)["UID_MAX"])

    uid_val = UIDRange(uid_min=uid_min, uid_max=uid_max)

    return uid_val
