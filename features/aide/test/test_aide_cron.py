from helper.utils import execute_remote_command


def test_aide_cron(client):
    # This will already fail if file is absent
    out = execute_remote_command(client, "cat /var/spool/cron/crontabs/root")
    # Validate that aide gets called (cron times may vary)
    assert "/usr/bin/aide --check --config /etc/aide/aide.conf" in out
