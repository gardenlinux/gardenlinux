import json
import pytest
from helper.sshclient import RemoteClient

def test_systemctl_no_failed_units(client, non_chroot, non_kvm):
    """this test always fails on kvm therefore kvm has it's own, chroot does not use systemd"""
    (exit_code, output, error) = client.execute_command("systemctl list-units --output=json --state=failed")
    assert exit_code == 0, f"no {error=} expected"
    out = (json.loads(output))
    failed_units = []

    for entry in out:
        failed_units.append(entry['unit'])

    for unit in failed_units:
        (log_exit_code, log_output, log_error) = client.execute_command(f"journalctl --no-pager -u {unit}")
        print(log_output)
        if log_exit_code != 0:
            print(f"journalctl failed to receive logs for unit {unit}. exited with {log_exit_code}")
            print(log_error)

    assert len(failed_units) == 0, f"systemd units {', '.join(failed_units)} failed"


def test_systemctl_no_failed_units_kvm(client, kvm):
    """rngd.service does not start in kvm due of missing /dev/tpm0"""
    (exit_code, output, error) = client.execute_command("systemctl list-units --output=json --state=failed")
    assert exit_code == 0, f"no {error=} expected"
    out = (json.loads(output))
    failed_units = []
    for entry in out:
        if not entry['unit'] == "rngd.service":
            failed_units.append(entry['unit'])

    for unit in failed_units:
        (log_exit_code, log_output, log_error) = client.execute_command(f"journalctl --no-pager -u {unit}")
        print(log_output)
        if log_exit_code != 0:
            print(f"journalctl failed to receive logs for unit {unit}. exited with {log_exit_code}")
            print(log_error)

    assert len(failed_units) == 0, f"systemd units {', '.join(failed_units)} failed"
