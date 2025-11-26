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
def test_dmesg_gardener_sysctl_no_restrictions_on_accessing_dmesg(file_content):
    file_path = "/etc/sysctl.d/40-allow-nonroot-dmesg.conf"
    result = file_content.get_mapping(
        file_path,
        {"kernel.dmesg_restrict": "0"},
        format="keyval",
    )
    assert result is not None, f"Could not parse file: {file_path}"
    assert result.all_match, (
        f"Could not find expected mapping in {file_path}: "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


@pytest.mark.feature("server and not gardener")
def test_dmesg_server_sysctl_restrictions_on_accessing_dmesg(file_content):
    file_path = "/etc/sysctl.d/40-restric-dmesg.conf"
    result = file_content.get_mapping(
        file_path,
        {"kernel.dmesg_restrict": "1"},
        format="keyval",
    )
    assert result is not None, f"Could not parse file: {file_path}"
    assert result.all_match, (
        f"Could not find expected mapping in {file_path}: "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


@pytest.mark.feature("stig")
def test_dmesg_stig_sysctl_restrictions_on_accessing_dmesg(file_content):
    file_path = "/etc/sysctl.d/99-stig.conf"
    result = file_content.get_mapping(
        file_path,
        {"kernel.dmesg_restrict": "1"},
        format="keyval",
    )
    assert result is not None, f"Could not parse file: {file_path}"
    assert result.all_match, (
        f"Could not find expected mapping in {file_path}: "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


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
    res = shell("dmesg", capture_output=True, ignore_exit_code=True)
    assert res.returncode == 0


@pytest.mark.feature("server and not gardener")
@pytest.mark.booted(reason="needs a booted system with dmesg restrictions loaded")
def test_dmesg_server_call_by_unprivileged_user_forbidden(shell):
    res = shell("dmesg", capture_output=True, ignore_exit_code=True)
    assert res.returncode == 1


@pytest.mark.feature("stig")
@pytest.mark.booted(reason="needs a booted system with dmesg restrictions loaded")
def test_dmesg_stig_call_by_unprivileged_user_forbidden(shell):
    res = shell("dmesg", capture_output=True, ignore_exit_code=True)
    assert res.returncode == 1
