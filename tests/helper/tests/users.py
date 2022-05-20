import helper.utils as utils

def users(client):
    # Get content from /etc/passwd
    (exit_code, output, error) = client.execute_command(
        "getent passwd", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    for line in output.split('\n'):
        # Ignore empty newline
        if line != '':
            line = line.split(":")

            user = line[0]
            uid = int(line[2])
            gid = int(line[3])
            shell = line[6]
            # There should NOT be any user present
            # except of 'dev' from dev feature or 'nobody' from nfs
            # https://github.com/gardenlinux/gardenlinux/issues/854
            if uid >= 1000:
                assert user in ["dev", "nobody"], \
                    f"Unexpected user account found in /etc/passwd: {user}"

            # Serviceaccounts should NOT have a valid shell
            # except of 'root' (gid: 0) and 'sync' (gid: 65534)
            # https://github.com/gardenlinux/gardenlinux/issues/814
            if uid < 1000:
                assert shell in ['/usr/sbin/nologin', '/bin/false'] \
                        or gid in [0, 65534], ("Unexpected shell found in " +
                                    f"/etc/passwd for user/service: {user}")

    # Permissions for '/root' should be set to 700
    # https://github.com/gardenlinux/gardenlinux/issues/813
    perm_root = utils.get_file_perm(client, '/root')
    perm_root_allow = 700
    assert perm_root == perm_root_allow, ("Directory /root is not set to " +
                                            f"{perm_root_allow}")
