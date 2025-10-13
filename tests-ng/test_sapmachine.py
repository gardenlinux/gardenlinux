import pytest
from plugins.dpkg import Dpkg
from plugins.apt import Apt
from plugins.shell import ShellRunner


@pytest.mark.feature("sapmachine")
def test_sapmachine_is_installed(dpkg: Dpkg):
    assert dpkg.package_is_installed(
        "sapmachine-25-jre-headless"
    ), "sapmachine-25-jre-headless package is not installed"


@pytest.mark.feature("sapmachine")
def test_java_version_command(shell: ShellRunner):
    out = shell("java -version", capture_output=True)
    assert "SapMachine" in out.stderr, "Expected jvm to be installed is SapMachine"


@pytest.mark.feature("sapmachine")
def test_sapmachine_apt_repo_is_installed(apt: Apt):
    repos = apt.list_repos()
    assert any(
        "sapmachine" in repo for repo in repos
    ), "No apt repo containing 'sapmachine' found"
