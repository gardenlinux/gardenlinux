import logging
import os
import pytest
import yaml

from .sshclient import RemoteClient

LYNIS_VER = "3.0.7"

logger = logging.getLogger(__name__)

def test_download_lynis(client):
    (exit_code, output, error) = client.execute_command("wget -O /tmp/lynis.tar.gz https://downloads.cisofy.com/lynis/lynis-{LYNIS_VER}.tar.gz".format(LYNIS_VER=LYNIS_VER))
    assert exit_code == 0, f"no {error=} expected"

def test_unarchive_lynis(client):
    (exit_code, output, error) = client.execute_command("tar xfvz /tmp/lynis.tar.gz")
    assert exit_code == 0, f"no {error=} expected"

def test_lynis_cis(client):
    # Unfortunately we need to change to the
    # lynis dir before we may execute lynis
    (exit_code, output, error) = client.execute_command("cd /root/lynis/ && /root/lynis/lynis audit system")
