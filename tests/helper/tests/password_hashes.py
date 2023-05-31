import re

def password_hashes(client):
    """Check configured password hashes"""
    # Call binary on remote and get content of file
    (exit_code, output, error) = client.execute_command(
        "cat /etc/pam.d/common-password", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    # Validate that the main part is present
    match_list = []
    for line in output.split('\n'):
        # success=n specifies to skip the next n lines during config parsing.
        # sssd uses success=2, and adds 2 fallback lines in case of non success.
        # but non-sssd default is success=1
        if re.search("^.*\[success=. default=ignore\].*", line):
            # Do not fetch comments
            if not line.startswith("#"):
                match_list.append(line)
                test_line = line

    # Validate that this is only defined a single time
    # to ensure no feature has appended different options
    # multiple times
    assert len(match_list) == 1, \
        "Redundant options defined in /etc/pam.d/common-password"

    # Validate the entry for 'sha512' or 'yescrypt'
    assert 'yescrypt' in test_line or 'sha512' in test_line, \
        f"No yescrypt or sha512 found in /etc/pam.d/common-password"