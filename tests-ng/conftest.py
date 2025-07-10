import os
import pwd
import pytest
import subprocess

pytest_plugins = [
	"features",
	"shell",
	"sysctl"
]

system_booted = False

def pytest_addoption(parser):
	parser.addoption(
		"--system-booted",
		action="store_true",
		help="Set if the system under test was booted instead of running in a chroot or container. This will enable kernel, systemd, and other system level tests."
	)

def pytest_configure(config):
	global system_booted
	system_booted = config.getoption("--system-booted")

	config.addinivalue_line("markers", "booted: mark test to run only on a booted target, i.e. not in a container or chroot")

def pytest_collection_modifyitems(config, items):
	for item in items:
		if item.get_closest_marker("booted") and not system_booted:
			pytest.mark.skip(reason="not running on a booted system")
