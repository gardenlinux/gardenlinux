def password_shadow(client):
    """check that no passwords are set in /etc/shadow or /etc/passwd"""
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