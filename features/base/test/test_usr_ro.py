
def test_usr_read_only(client, non_provisioner_chroot):
    (exit_code, output, error) = client.execute_command("/usr/bin/touch /usr/fail-test")
    assert exit_code == 1, "Read-only file system error expected"
    assert error.rstrip() == "/usr/bin/touch: cannot touch '/usr/fail-test': Read-only file system"
