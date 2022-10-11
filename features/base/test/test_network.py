import pytest
import datetime
from helper.sshclient import RemoteClient


def test_hostname_azure(client, azure):
    """ Test for valid hostname on azure platform """
    start_time = datetime.datetime.now()
    (exit_code, output, error) = client.execute_command("nslookup $(hostname)")
    assert exit_code == 0, f"no {error=} expected"
    end_time = datetime.datetime.now()
    time_diff = (end_time - start_time)
    execution_time = round(time_diff.total_seconds())
    assert execution_time <= 2, f"nslookup should not run in a timeout {error}"


@pytest.fixture(params=["8.8.8.8", "dns.google", "heise.de"])
def ping4_host(request):
    return request.param

def test_ping4(client, ping4_host, non_chroot, non_kvm):
    """ Test if destination by fixture in pingable (IPv4) """
    command = f"ping -c 5 -W 5 {ping4_host}"
    (exit_code, output, error) = client.execute_command(command)
    assert exit_code == 0, f'no {error=} expected when executing "{command}"'
    assert "5 packets transmitted, 5 received, 0% packet loss" in output


@pytest.fixture(params=["2001:4860:4860::8888", "dns.google", "heise.de"])
def ping6_host(request):
    return request.param

@pytest.mark.skip(reason="ipv6 not available in all vpcs")
def test_ping6(client, ping6_host):
    """ Test if destination by fixture in pingable (IPv6) """
    command = f"ping6 -c 5 -W 5 {ping6_host}"
    (exit_code, output, error) = client.execute_command(command)
    assert exit_code == 0, f'no {error=} expected when executing "{command}"'
    assert "5 packets transmitted, 5 received, 0% packet loss" in output
