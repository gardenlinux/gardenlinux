from helper.utils import execute_remote_command


def test_aide_cron(client):
    # This will already fail if file is absent
    rc, out = execute_remote_command(client, "cat /var/spool/cron/crontabs/root")
    # Validate that aide gets called (cron times may vary)
    err_msg = "Cron configuration for AIDE expected but could not be verified."
    assert "/usr/bin/aide --check --config /etc/aide/aide.conf" in out and rc == 0, f"{err_msg} Error: {out}"
