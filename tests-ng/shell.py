import os
import pwd
import pytest
import subprocess

default_user = None

class ShellRunner:
	def __init__(self, user):
		self.user = user
	
	def __call__(self, cmd, capture_output=False):
		def _setuid():
			if self.user != None:
				os.setgid(self.user[1])
				os.setuid(self.user[0])

		result = subprocess.run(['/bin/sh', '-e', '-c', cmd], shell=False, capture_output=capture_output, text=True, check=False, preexec_fn=_setuid)

		if result.returncode != 0:
			raise RuntimeError(f"command {cmd} failed with exit code {result.returncode}")

		return result

def pytest_addoption(parser):
	parser.addoption(
		"--default-user",
		action="store",
		default="",
		help="User to switch to before executing shell commands"
	)

def pytest_configure(config):
	global default_user

	default_user_name = config.getoption("--default-user")
	if default_user_name != "":
		passwd_entry = pwd.getpwnam(default_user_name)
		default_user = (passwd_entry.pw_uid, passwd_entry.pw_gid)
	if default_user == None and os.geteuid() == 0:
		default_user = (65534, 65534)

	config.addinivalue_line("markers", "root: mark test to run as root user")

@pytest.fixture
def shell(request):
	root_marker = bool(request.node.get_closest_marker("root"))
	if root_marker:
		if os.geteuid() != 0:
			pytest.skip("tests marked as root but running as unprivileged user")
		return ShellRunner((0, 0))
	else:
		return ShellRunner(default_user)
