import pytest

system_booted = False

def pytest_configure(config):
	global system_booted
	system_booted = config.getoption("--system-booted")

class SysctlWrapper:
	def __getitem__(self, key):
		path = "/proc/sys/" + key.replace(".", "/")
		with open(path, "r") as f:
			value = f.read().strip()
		return int(value) if value.isdigit() else value

@pytest.fixture
def sysctl(request):
	if not system_booted:
		pytest.skip("sysctl only available when running on booted system")
	return SysctlWrapper()
