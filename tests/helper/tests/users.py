import helper.utils as utils


def users(client, additional_user = "", additional_sudo_users=[]):
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
                assert user in ["dev", "nobody", additional_user], \
                    f"Unexpected user account found in /etc/passwd: {user}"

            # Serviceaccounts should NOT have a valid shell
            # except of 'root' (gid: 0) and 'sync' (gid: 65534)
            # https://github.com/gardenlinux/gardenlinux/issues/814
            if uid < 1000:
                assert shell in ['/usr/sbin/nologin', '/bin/false'] \
                        or gid in [0, 65534], ("Unexpected shell found in " +
                                    f"/etc/passwd for user/service: {user}")

            # Test for sudo priviledges for each user 
            # (additional users may have sudo access)
            additional_sudo_users.append("root")
            if user not in additional_sudo_users:
                _has_user_sudo_cmd(client, user)

    # Permissions for '/root' should be set to 700
    # https://github.com/gardenlinux/gardenlinux/issues/813
    perm_root = utils.get_file_perm(client, '/root')
    perm_root_allow = 700
    assert perm_root == perm_root_allow, ("Directory /root is not set to " +
                                            f"{perm_root_allow}")

    # There should NOT be any (abdondend) home directory present
    # except of 'dev' from dev feature. User (uid >= 1000)
    # with custom home directories are already handled within
    # this PyTest earlier.
    # https://github.com/gardenlinux/gardenlinux/issues/826
    (exit_code, output, error) = client.execute_command(
         "ls /home/", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    permitted_homes = [ '', additional_user ]
    discovered_homes = []
    for line in output.split('\n'):
        if line not in permitted_homes:
            discovered_homes.append(line)
    assert len(discovered_homes) == 0, f"Found the following home directories: {discovered_homes}"


def _has_user_sudo_cmd(client, user):
    """ Check if user has any sudo permissions """

    # make sure executing user is in wheel group
    cmd = "usermod -a -G wheel $(whoami)"
    out = utils.execute_remote_command(client, cmd)

    # Execute command on remote platform
    cmd = f"sudo -l -U {user}"
    out = utils.execute_remote_command(client, cmd)

    # Write each line as output in list
    output_lines = []
    for line in out.split("\n"):
       output_lines.append(line)

    # Check if there is enough content in our list
    # and validate if there are related sudo commands
    sudo_cmd = False
    if len(output_lines) > 3:
        if "may run the following commands on" in output_lines[-2]:
           sudo_cmd = output_lines[-1]

    assert not sudo_cmd, f"User: {user} has sudo permissions for: {sudo_cmd}"
