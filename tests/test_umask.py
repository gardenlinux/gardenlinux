import pytest
from plugins.parse_file import ParseFile
from plugins.shell import ShellRunner


@pytest.mark.setting_ids(["GL-SET-base-config-login-defs"])
def test_umask_file(parse_file: ParseFile):
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert config["UMASK"] == "027"


@pytest.mark.setting_ids(["GL-SET-base-config-login-defs"])
@pytest.mark.root
def test_umask_cmd(shell: ShellRunner):
    result = shell("su --login --command 'umask'", capture_output=True)
    assert result.returncode == 0, f"Could not execute umask cmd: {result.stderr}"
    assert result.stdout == "0027\n", "umask is not set to 0027"
