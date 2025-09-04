import datetime
import socket
import threading
import pytest


def has_ipv6():
    """Helper function to detect IPv6 availability."""
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.close()
        return True
    except OSError:
        return False


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


@pytest.mark.parametrize("family,loopback", LOCAL_TEST_PARAMS)
def test_local_tcp_stack(family, loopback):
    """
    Test if local TCP stack is functional by creating a new
    listening socket on the loopback device and connecting to it.
    """
    # Arrange
    msg = b"hello"
    result = {}

    def server():
        with socket.socket(family, socket.SOCK_STREAM) as s:
            s.bind((loopback, 0))
            port = s.getsockname()[1]  # Get automatically chosen port
            result["port"] = port
            s.listen(1)
            conn, _ = s.accept()
            data = conn.recv(1024)
            result["data"] = data

    thread = threading.Thread(target=server, daemon=True)
    thread.start()

    # Wait for server port to be ready
    while "port" not in result:
        pass

    # Act
    with socket.create_connection((loopback, result["port"]), timeout=2) as c:
        c.sendall(msg)

    thread.join(timeout=2)
    # Assert
    assert result.get("data") == msg


@pytest.mark.parametrize("family,loopback", LOCAL_TEST_PARAMS)
def test_local_udp_stack(family, loopback):
    """
    Test if local UDP stack is functional by creating a new listening
    socket on the loopback device and sending data to it.
    """
    # Arrange
    server = socket.socket(family, socket.SOCK_DGRAM)
    server.bind((loopback, 0))
    addr, port = server.getsockname()[:2]

    client = socket.socket(family, socket.SOCK_DGRAM)

    # Act / Assert
    client.sendto(b"ping", (addr, port))
    data, src = server.recvfrom(1024)
    assert data == b"ping"

    server.sendto(b"pong", src)
    data, _ = client.recvfrom(1024)
    assert data == b"pong"

    # Clean
    client.close()
    server.close()


@pytest.mark.booted
def test_resolv_conf_exists(shell):
    """Test if local DNS config is available."""
    result = shell("test -s /etc/resolv.conf", ignore_exit_code=True)
    assert result.returncode == 0, "/etc/resolv.conf is missing or empty."


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
