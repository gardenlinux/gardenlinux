import pytest
from plugins.parse_file import ParseFile
from plugins.shell import ShellRunner


def test_umask_file(parse_file: ParseFile):
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert config["UMASK"] == "027"


@pytest.mark.root
@pytest.mark.feature("not cis", reason="CIS needs umask 0027")
def test_umask_cmd(shell: ShellRunner):
    result = shell("su --login --command 'umask'", capture_output=True)
    assert result.returncode == 0, f"Could not execute umask cmd: {result.stderr}"
    assert result.stdout == "0027\n", "umask is not set to 0027"
