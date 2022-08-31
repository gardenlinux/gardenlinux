from helper.utils import execute_remote_command


def test_clamav_cron(client):
    # This will already fail if file is absent
    rc, out = execute_remote_command(client, "cat /var/spool/cron/crontabs/root", skip_error=True)
    # Validate that clamscan gets called (cron times may vary)
    err_msg = "Cron configuration for ClamAV expected but could not be verified."
    assert "clamscan" in out and rc == 0, f"{err_msg} Error: {out}"
