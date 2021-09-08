import json
import logging
import os
import time
from pathlib import Path
from typing import Iterator

import pytest
import yaml

from .aws import AWS
from .gcp import GCP
from .azure import AZURE
from .sshclient import RemoteClient

logger = logging.getLogger(__name__)
giaas = None

@pytest.fixture(scope="module")
def config(configFile):
    try:
        if os.path.exists(configFile):
            realName = configFile
        else:
            root = Path(os.path.dirname(os.path.abspath(__file__))).parent
            realName = root.joinpath(configFile)
        with open(realName) as f:
            options = yaml.load(f, Loader=yaml.FullLoader)
    except OSError as e:
        logger.exception(e)
        exit(1)
    yield options


@pytest.fixture(scope="module")
def client(request, config: dict, iaas) -> Iterator[RemoteClient]:
    logger.info(config)
    if iaas == "aws":
        yield from AWS.fixture(config["aws"])
    elif iaas == "gcp":
        yield from GCP.fixture(config["gcp"])
    elif iaas == "azure":
        yield from AZURE.fixture(config["azure"])
    else:
        raise ValueError(f"invalid {iaas=}")


@pytest.fixture(scope='module')
def non_azure(iaas):
    if iaas == 'azure':
        pytest.skip('test not supported on azure')


@pytest.fixture(scope='module')
def azure(iaas):
    if iaas != 'azure':
        pytest.skip('test only supported on azure')


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


def test_metadata_connection_non_az(client, non_azure):
    metadata_host = "169.254.169.254"
    (exit_code, output, error) = client.execute_command(
        f"wget --timeout 5 http://{metadata_host}"
    )
    assert exit_code == 0, f"no {error=} expected"
    assert f"Connecting to {metadata_host}:80... connected." in error
    assert "200 OK" in error
 

def test_metadata_connection_az(client, azure):

    metadata_url = "http://169.254.169.254/metadata/instance/compute?api-version=2021-01-01&format=json"
    (exit_code, output, error) = client.execute_command(
        f"curl --connect-timeout 5 '{metadata_url}' -H 'Metadata: true'"
    )
    assert exit_code == 0, f"no {error=} expected"


@pytest.fixture(params=["8.8.8.8", "dns.google", "heise.de"])
def ping4_host(request):
    return request.param


def test_ping4(client, ping4_host):
    command = f"ping -c 5 -W 5 {ping4_host}"
    (exit_code, output, error) = client.execute_command(command)
    assert exit_code == 0, f'no {error=} expected when executing "{command}"'
    assert "5 packets transmitted, 5 received, 0% packet loss" in output


@pytest.fixture(params=["2001:4860:4860::8888", "dns.google", "heise.de"])
def ping6_host(request):
    return request.param

@pytest.mark.skip(reason="ipv6 not available in all vpcs")
def test_ping6(client, ping6_host):
    command = f"ping6 -c 5 -W 5 {ping6_host}"
    (exit_code, output, error) = client.execute_command(command)
    assert exit_code == 0, f'no {error=} expected when executing "{command}"'
    assert "5 packets transmitted, 5 received, 0% packet loss" in output

def test_systemctl_no_failed_units(client):
    (exit_code, output, error) = client.execute_command("systemctl list-units --output=json --state=failed")
    assert exit_code == 0, f"no {error=} expected"
    assert len(json.loads(output)) == 0

def test_startup_time(client):
    tolerated_startup_time = 60
    (exit_code, output, error) = client.execute_command("systemd-analyze")
    assert exit_code == 0, f"no {error=} expected"
    lines = output.splitlines()
    items = lines[0].split(" ")
    time=items[12]
    tf = float(time[:-1])
    assert tf < tolerated_startup_time, f"startup time too long: {tf}seconds but only {tolerated_startup_time} tolerated."

def test_growpart(client):
    (exit_code, output, error) = client.execute_command("df --output=size -BG /")
    assert exit_code == 0, f"no {error=} expected"
    lines = output.splitlines()
    sgb = int(lines[1].strip()[:-1])
    assert sgb == 6, f"partition size expected to be ~6 GB but is {sgb}"

def test_docker(client):
    (exit_code, output, error) = client.execute_command("sudo systemctl enable docker")
    assert exit_code == 0, f"no {error=} expected"
    (exit_code, output, error) = client.execute_command("sudo docker run --rm  alpine:3.14.2 sh -c 'echo from container'")
    assert exit_code == 0, f"no {error=} expected"
    assert output == "from container\n", f"Expected 'from container' output but got {output}"
