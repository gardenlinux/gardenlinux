import pytest
from plugins.sysctl import Sysctl


@pytest.mark.feature("server")
@pytest.mark.booted(reason="runtime knobs are applied at boot")
def test_memory(sysctl: Sysctl):
    assert sysctl["vm.max_map_count"] == 2147483647
    assert sysctl["kernel.shmmni"] == 32768


@pytest.mark.feature("server")
@pytest.mark.booted(reason="runtime knobs are applied at boot")
def test_network(sysctl: Sysctl):
    assert sysctl["net.ipv4.tcp_keepalive_time"] == 300
    assert sysctl["net.ipv4.tcp_max_syn_backlog"] == 8192
