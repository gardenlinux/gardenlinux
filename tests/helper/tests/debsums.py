from helper import utils

def debsums(client, debsums_exclude):
    """Check the MD5 sums of installed Debian packages"""
    utils.AptUpdate(client)
    utils.install_package_deb(client, "debsums")

    (exit_code, output, error) = client.execute_command("debsums -l",
                                                        quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    assert output == '', \
                    f"the following packages don't have md5sums: {output}"

    (exit_code, output, error) = client.execute_command("debsums -sc",
                                                        quiet=True)
    assert exit_code == 0 or exit_code == 2, f"no {error=} expected"

    changed = []
    for line in error.splitlines():
        if line.split()[3] not in debsums_exclude:
            changed.append(line.split()[3] + " " + line.split()[4] +
                " " + line.split()[5] + " " + line.split()[6])

    assert len(changed) == 0, \
                f"the following files have changes: {', '.join(changed)}"
