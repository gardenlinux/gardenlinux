from helper.utils import get_file_perm

def password_shadow(client):
    """check that no passwords are set in /etc/shadow or /etc/passwd"""
    _check_file_permssions(client)
    (exit_code, output, error) = client.execute_command(
        "getent shadow", quiet=True)
    assert exit_code == 0, f"no {error=} expected"
    assert _check_format(output, ["*", "!"]), \
                            "No passwords should be set in /etc/shadow"

    (exit_code, output, error) = client.execute_command(
        "getent passwd", quiet=True)
    assert exit_code == 0, f"no {error=} expected"
    assert _check_format(output, ["*", "x"]), \
                            "Malformed entries in /etc/passwd"

def _check_format(input: str, expected: list):
    """check format of the password in /etc/shadow or /etc/passwd"""
    for line in input.splitlines():
        password = line.split(":")[1]
        if not password[0] in expected:
            return False
    return True


def _check_file_permssions(client):
    passwd_perm = get_file_perm(client, '/etc/passwd')
    assert 644 == passwd_perm, "/etc/passwd has the wrong permissions!"

    group_perm = get_file_perm(client, '/etc/group')
    assert 644 == group_perm, "/etc/group has the wrong permissions!"

    shadow_perm = get_file_perm(client, '/etc/shadow')
    assert 640 == shadow_perm, "/etc/shadow has the wrong permissions!"

    gshadow_perm = get_file_perm(client, '/etc/gshadow')
    assert 640 == shadow_perm, "/etc/gshadow has the wrong permissions!"
