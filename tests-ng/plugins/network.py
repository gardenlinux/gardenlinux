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


@pytest.fixture
def tcp_echo_server():
    """
    Creates a simple TCP echo server on the loopback interface.
    Yields (ip_version, loopback, port, result_dict).
    """
    servers = []

    def _start(ip_version, loopback, msg=b"Hello, TCP!"):
        result = {}

        def server():
            with socket.socket(ip_version, socket.SOCK_STREAM) as s:
                s.bind((loopback, 0))
                port = s.getsockname()[1]
                result["port"] = port
                s.listen(1)
                conn, _ = s.accept()
                data = conn.recv(1024)
                result["data"] = data

        thread = threading.Thread(target=server, daemon=True)
        thread.start()
        servers.append((thread, result, msg))
        return result

    yield _start

    # Teardown: join all threads
    for thread, result, _ in servers:
        thread.join(timeout=2)


@pytest.fixture
def udp_echo_server():
    """
    Creates a simple UDP echo server on the loopback interface.
    Yields (addr, port, result_dict)
    """
    servers = []

    def _start(ip_version, loopback):
        result = {}

        def server():
            with socket.socket(ip_version, socket.SOCK_DGRAM) as s:
                s.bind((loopback, 0))
                addr, port = s.getsockname()[:2]
                result["addr"] = addr
                result["port"] = port

                data, src = s.recvfrom(1024)
                result["data"] = data
                s.sendto(b"pong", src)

        thread = threading.Thread(target=server, daemon=True)
        thread.start()
        servers.append((thread, result))
        return result

    yield _start

    # Threadown: join all threads
    for thread, result in servers:
        thread.join(timeout=2)
