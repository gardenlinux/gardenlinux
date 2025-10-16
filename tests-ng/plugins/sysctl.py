import pytest
from plugins.booted import is_system_booted


class SysctlWrapper:
    def __getitem__(self, key: str):
        path = "/proc/sys/" + key.replace(".", "/")
        with open(path, "r") as f:
            value = f.read().strip()
        return int(value) if value.isdigit() else value


@pytest.fixture
def sysctl(request: pytest.FixtureRequest):
    if not is_system_booted():
        pytest.skip("sysctl only available when running on booted system")
    return SysctlWrapper()
