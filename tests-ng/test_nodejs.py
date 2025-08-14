import pytest
from plugins.dpkg import Dpkg
from plugins.shell import ShellRunner


@pytest.mark.feature("nodejs")
def test_nodejs_is_installed(shell: ShellRunner):
    dpkg = Dpkg(shell)
    assert dpkg.package_is_installed(
        "nodejs"
    ), "nodejs package is not installed"


@pytest.mark.feature("nodejs")
def test_node_can_run_script(shell: ShellRunner):
    out = shell("node --eval 'const foo = (x,y) => x + y; console.log(foo(1,2))'", capture_output=True)
    assert out.stdout == '3\n', "Expected node to run script"
