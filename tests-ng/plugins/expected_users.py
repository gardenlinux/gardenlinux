import pytest

users = []

def pytest_addoption(parser):
	parser.addoption(
		"--expected-users",
		action="store",
		default="",
		help="List of expected users (comma separated)"
	)

def pytest_configure(config):
	global users
	arg = config.getoption("--expected-users")
	if arg:
		users = [u.strip() for u in arg.split(",") if u.strip()]

@pytest.fixture
def expected_users():
	return users
