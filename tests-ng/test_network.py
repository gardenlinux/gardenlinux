import os
import datetime
import socket
import threading
import pytest

from plugins.network import has_ipv6


# Test parameters. IPv6 skipped if not supported.
LOCAL_TEST_PARAMS = [
    pytest.param(socket.AF_INET, "127.0.0.1"),
    pytest.param(
        socket.AF_INET6,
        "::1",
        marks=pytest.mark.skipif(not has_ipv6(), reason="IPv6 not available"),
    ),
]


@pytest.mark.booted(reason="ping requires full network stack")
def test_loopback_interface(shell):
    """Assert loopback device present."""
    result = shell("ping -c 1 127.0.0.1", capture_output=True)
    assert result.returncode == 0
    assert "1 received" in result.stdout


@pytest.mark.parametrize("ip_version, loopback", LOCAL_TEST_PARAMS)
def test_local_tcp_stack(ip_version, loopback, tcp_echo_server):
    """
    Test if local TCP stack is functional by creating a new
    listening socket on the loopback device and connecting to it.
    """
    # Arrange
    msg = b"Hello, TCP!"
    result, done = tcp_echo_server(ip_version, loopback, msg)

    # Wait until the server bound to a port
    while "port" not in result:
        pass

    # Act
    with socket.create_connection((loopback, result["port"]), timeout=2) as conn:
        conn.sendall(msg)

    # Assert
    done.wait(timeout=2)
    assert result.get("data") == msg


@pytest.mark.parametrize("ip_version,loopback", LOCAL_TEST_PARAMS)
def test_local_udp_stack(ip_version, loopback, udp_echo_server):
    """
    Test if local UDP stack is functional by creating a new listening
    socket on the loopback device and sending data to it.
    """
    # Arrange
    msg = b"ping"
    result = udp_echo_server(ip_version, loopback)

    # Wait until the server bound to a port
    while "port" not in result:
        pass

    # Act
    with socket.socket(ip_version, socket.SOCK_DGRAM) as client:
        client.sendto(msg, (result["addr"], result["port"]))
        reply_data, _ = client.recvfrom(1024)

        # Assert
        assert result.get("data") == msg
        assert reply_data == b"pong"


@pytest.mark.booted
def test_resolv_conf_exists():
    """Test if local DNS config is available."""
    # Arrange
    path = "/etc/resolv.conf"

    # Act / Assert
    assert os.path.isfile(path), f"'{path}' does not exist or is not a file"
    assert os.path.getsize(path) > 0, f"'{path}' is empty"


@pytest.mark.booted
def test_no_default_drop_policy(shell):
    result = shell(
        "iptables -S | grep 'DROP'", capture_output=True, ignore_exit_code=True
    )
    assert "DROP" not in result.stdout, "Default DROP policy detected"


@pytest.mark.booted(reason="nslookup requires fully booted system")
@pytest.mark.feature("azure")
def test_hostname_azure(shell):
    """Test if hostname is resolvable in Azure DNS."""
    # Arrange / Act
    start_time = datetime.datetime.now()
    result = shell("nslookup $(hostname)", capture_output=True, ignore_exit_code=True)
    end_time = datetime.datetime.now()

    # Assert
    assert result.returncode == 0, f"nslookup failed: {result.stderr}"

    execution_time = round((end_time - start_time).total_seconds())
    assert (
        execution_time <= 10
    ), f"nslookup should not run into timeout: {result.stderr}"
