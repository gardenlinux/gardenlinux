import logging

logger = logging.getLogger(__name__)

def capabilities(client, capabilities):
    """ Test if only the defined capabilities are set"""
    (exit_code, output, error) = client.execute_command(
        "find /boot /etc /usr /var -type f -exec getcap {} \\;", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    cap_notfound = []
    for line in output.splitlines():
        if line not in capabilities:
            cap_notfound.append(line)

    assert len(cap_notfound) == 0, ("Capabilities " +
        f"{', '.join(cap_notfound)} are not in expected capabilities list")
