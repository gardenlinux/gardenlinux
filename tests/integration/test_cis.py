import logging
import os
import pytest
import yaml

from .sshclient import RemoteClient

LYNIS_VER = "3.0.7"
LYNIS_REPORT = "/var/log/lynis-report.dat"
logger = logging.getLogger(__name__)

def test_download_lynis(client):
    (exit_code, output, error) = client.execute_command("wget -O /tmp/lynis.tar.gz https://downloads.cisofy.com/lynis/lynis-{LYNIS_VER}.tar.gz".format(LYNIS_VER=LYNIS_VER))
    assert exit_code == 0, f"no {error=} expected"

def test_unarchive_lynis(client):
    (exit_code, output, error) = client.execute_command("tar xfvz /tmp/lynis.tar.gz -C /tmp/")
    assert exit_code == 0, f"no {error=} expected"

def test_lynis_cis(client):
    # Unfortunately we need to change to the
    # lynis dir before we may execute lynis
    (exit_code, output, error) = client.execute_command("cd /tmp/lynis/ && /usr/bin/sh /tmp/lynis/lynis --no-log audit system > /tmp/lynis.output")
    assert exit_code == 0, f"no {error=} expected"

def test_lynis_output(client):
    (exit_code, output, error) = client.execute_command("cat /tmp/lynis.output")
    validation = False
    if "Great, no warnings" in output:
        validation = True
    assert validation

def test_lynis_log_warn(client):
    (exit_code, output, error) = client.execute_command(f"cat {LYNIS_REPORT}")
    validation = False
    if not "warning[]" in output:
        validation = True
    assert validation

def test_lynis_log_crit(client):
    (exit_code, output, error) = client.execute_command(f"cat {LYNIS_REPORT}")
    validation = False
    if not "critical[]" in output:
        validation = True
    assert validation
