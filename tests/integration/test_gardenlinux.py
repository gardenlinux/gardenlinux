import logging
import os
import time
from pathlib import Path
from typing import Iterator

import pytest
import yaml

from .aws import AWS
from .gcp import GCP
from .sshclient import RemoteClient

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def config():
    try:
        root = Path(os.path.dirname(os.path.abspath(__file__))).parent
        path = root.joinpath("test_config.yaml")
        with open(path) as f:
            options = yaml.load(f, Loader=yaml.FullLoader)
    except OSError as e:
        logger.exception(e)
        exit(1)
    yield options


@pytest.fixture(scope="module", params=["aws", "gcp"])
def client(request, config: dict) -> Iterator[RemoteClient]:
    if request.param == "aws":
        yield from AWS.fixture(config["aws"])
    if request.param == "gcp":
        yield from GCP.fixture(config["gcp"])


def test_clock(client):
    (exit_code, output, error) = client.execute_command("date '+%s'")
    local_seconds = time.time()
    assert exit_code == 0, f"no {error=} expected"
    remote_seconds = int(output)
    assert (
        abs(local_seconds - remote_seconds) < 5
    ), "clock skew should be less than 5 seconds"


def test_ls(client):
    (exit_code, output, error) = client.execute_command("ls /")
    assert exit_code == 0, f"no {error=} expected"
    assert output
    lines = output.split("\n")
    assert "bin" in lines
    assert "boot" in lines
    assert "dev" in lines
    assert "etc" in lines
    assert "home" in lines
    assert "lib" in lines
    assert "lib64" in lines
    assert "mnt" in lines
    assert "opt" in lines
    assert "proc" in lines
    assert "root" in lines
    assert "run" in lines
    assert "sbin" in lines
    assert "srv" in lines
    assert "sys" in lines
    assert "tmp" in lines
    assert "usr" in lines
    assert "var" in lines


def test_no_man(client):
    (exit_code, _, error) = client.execute_command("man ls")
    assert exit_code == 127, '"man" should not be installed'
    assert "man: command not found" in error


def test_metadata_connection(client):
    metadata_host = "169.254.169.254"
    (exit_code, output, error) = client.execute_command(
        f"wget --timeout 5 http://{metadata_host}"
    )
    assert exit_code == 0, f"no {error=} expected"
    assert f"Connecting to {metadata_host}:80... connected." in error
    assert "200 OK" in error


@pytest.fixture(params=["4", "6"])
def ip_version(request):
    return request.param


@pytest.fixture(params=["8.8.8.8", "heise.de"])
def ping_host(request):
    return request.param


def test_ping(client, ip_version, ping_host):
    command = f"ping -{ip_version} -c 5 -W 5 {ping_host}"
    (exit_code, output, error) = client.execute_command(command)
    assert exit_code == 0, f'no {error=} expected when executing "{command}"'
    assert "5 packets transmitted, 5 received, 0% packet loss" in output
