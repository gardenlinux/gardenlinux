import json
import pytest
from helper.sshclient import RemoteClient

def test_systemctl_no_failed_units(client, non_chroot, non_kvm):
    """this test always fails on kvm therefore kvm has it's own, chroot does not use systemd"""
    (exit_code, output, error) = client.execute_command("systemctl list-units --output=json --state=failed")
    assert exit_code == 0, f"no {error=} expected"
    assert len(json.loads(output)) == 0


def test_systemctl_no_failed_units_kvm(client, kvm):
    """rngd.service does not start in kvm due of missing /dev/tpm0"""
    (exit_code, output, error) = client.execute_command("systemctl list-units --output=json --state=failed")
    assert exit_code == 0, f"no {error=} expected"
    out = (json.loads(output))
    error_count = 0
    error_out = []
    for entry in out:
        if not entry['unit'] == "rngd.service":
            error_count += 1
            error_out.append(entry['unit'])
    assert error_count == 0, f"systemd units {', '.join(error_out)} failed"
