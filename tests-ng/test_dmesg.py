import re
from pathlib import Path

import pytest

# server adds /etc/sysctl.d/40-restric-dmesg.conf, gardener excludes it
#    and adds /etc/sysctl.d/40-allow-nonroot-dmesg.conf instead


@pytest.mark.feature("gardener")
def test_dmesg_sysctl_gardener_config_file_exists():
    assert Path("/etc/sysctl.d/40-allow-nonroot-dmesg.conf").exists()


@pytest.mark.feature("server and not gardener")
def test_dmesg_sysctl_server_config_file_exists():
    assert Path("/etc/sysctl.d/40-restric-dmesg.conf").exists()


@pytest.mark.feature("stig")
def test_dmesg_sysctl_stig_config_file_exists():
    assert Path("/etc/sysctl.d/99-stig.conf").exists()


@pytest.mark.feature("gardener")
def test_dmesg_gardener_sysctl_no_restrictions_on_accessing_dmesg():
    pattern = re.compile(
        r"""
            ^\s*    # any whitespace in the beginning of the line is allowed
            (?!\#)  # fail the search if a comment character is found
            kernel\.dmesg_restrict\s*=\s*0
        """,
        re.VERBOSE | re.MULTILINE,
    )
    assert re.search(
        pattern, Path("/etc/sysctl.d/40-allow-nonroot-dmesg.conf").read_text()
    )


@pytest.mark.feature("server and not gardener")
def test_dmesg_server_sysctl_restrictions_on_accessing_dmesg():
    pattern = re.compile(
        r"""
            ^\s*    # any whitespace in the beginning of the line is allowed
            (?!\#)  # fail the search if a comment character is found
            kernel\.dmesg_restrict\s*=\s*1
        """,
        re.VERBOSE | re.MULTILINE,
    )
    assert re.search(pattern, Path("/etc/sysctl.d/40-restric-dmesg.conf").read_text())


@pytest.mark.feature("stig")
def test_dmesg_stig_sysctl_restrictions_on_accessing_dmesg():
    pattern = re.compile(
        r"""
            ^\s*    # any whitespace in the beginning of the line is allowed
            (?!\#)  # fail the search if a comment character is found
            kernel\.dmesg_restrict\s*=\s*1
        """,
        re.VERBOSE | re.MULTILINE,
    )
    assert re.search(pattern, Path("/etc/sysctl.d/99-stig.conf").read_text())


@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_dmesg_gardener_no_restrictions_sysctl_runtime(sysctl):
    assert sysctl["kernel.dmesg_restrict"] == "0"


@pytest.mark.feature("server and not gardener")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_dmesg_server_restrictions_sysctl_runtime(sysctl):
    assert sysctl["kernel.dmesg_restrict"] == "1"


@pytest.mark.feature("stig")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_dmesg_stig_restrictions_sysctl_runtime(sysctl):
    assert sysctl["kernel.dmesg_restrict"] == "1"


@pytest.mark.booted(reason="needs a booted system with dmesg restrictions loaded")
@pytest.mark.feature("gardener")
def test_dmesg_gardener_call_by_unprivileged_user_allowed(shell):
    res = shell("dmesg", capture_output=False, ignore_exit_code=True)
    assert res.returncode == 0


@pytest.mark.feature("server and not gardener")
@pytest.mark.booted(reason="needs a booted system with dmesg restrictions loaded")
def test_dmesg_server_call_by_unprivileged_user_forbidden(shell):
    res = shell("dmesg", capture_output=False, ignore_exit_code=True)
    assert res.returncode == 1


@pytest.mark.feature("stig")
@pytest.mark.booted(reason="needs a booted system with dmesg restrictions loaded")
def test_dmesg_stig_call_by_unprivileged_user_forbidden(shell):
    res = shell("dmesg", capture_output=False, ignore_exit_code=True)
    assert res.returncode == 1
