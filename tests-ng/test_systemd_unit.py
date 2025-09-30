import pytest
from plugins.shell import ShellRunner
from plugins.dpkg import Dpkg


def validate_systemd_unit(shell: ShellRunner, systemd_unit, active=True):
    """ Validate a given systemd unit """
    cmd = f"systemctl status {systemd_unit}.service"
    output = shell(cmd, capture_output=True)

    assert output.returncode == 0, f"systemd-unit: {systemd_unit} exited with {output.returncode}."
    # Validate output lines of systemd-unit
    for line in output.stdout.splitlines():
        # This 'active' is realted to systemd's output
        if "Active:" in line:
            # This active is set by the function's header
            if active:
                assert not "dead" in line, f"systemd-unit: {systemd_unit} did not start."
            else:
                assert "condition failed" in line, f"systemd-unit: {systemd_unit} condition for architecture failed."


@pytest.mark.parametrize(
    "systemd_unit",
    [
        pytest.param("kubelet", marks=pytest.mark.feature("chost or khost", reason="kubelet required for chost and khost")),
        pytest.param("nftables", marks=pytest.mark.feature("firewall", reason="nftables required for firewall")),
        pytest.param("containerd", marks=pytest.mark.feature("gardener", reason="containerd required for gardener")),
        pytest.param("libvirtd", marks=pytest.mark.feature("vhost", reason="libvirtd required for vhost"))
    ],
)
@pytest.mark.booted(reason="Test runs systemd")
@pytest.mark.root(reason="To start the systemd service")
@pytest.mark.modify(reason="Starts systemd service")
def test_systemd_unit(shell: ShellRunner, systemd_unit):
    shell(f"systemctl start {systemd_unit}")
    validate_systemd_unit(shell, systemd_unit)


@pytest.mark.booted(reason="Test runs systemd")
@pytest.mark.root(reason="To start the systemd service")
@pytest.mark.modify(reason="Starts systemd service")
@pytest.mark.feature("firecracker", reason="rngd required for firecracker")
def test_systemd_rngd(shell: ShellRunner, dpkg: Dpkg):
    arch = dpkg.get_architecture()
    active = True

    # We assume that on arm64, the systemd
    # unit should not be active after a start
    if arch == "arm64":
        active = False

    shell("systemctl start rngd")
    validate_systemd_unit(shell, "rngd", active=active)
