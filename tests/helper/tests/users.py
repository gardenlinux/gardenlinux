import helper.utils as utils
import helper.tests.groups as groups
from helper.tests.mount import _parse_fstab
from helper.utils import check_file, get_file_perm


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

    (exit_code, output, error) = client.execute_command("[ -L /home ] && echo 'symlink' || echo 'not_symlink'", quiet=True)
    if exit_code == 0 and output.strip() == 'symlink':
        return

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

    
    _users_home(client, additional_user)


def _has_user_sudo_cmd(client, user):
    """ Check if user has any sudo permissions """

    # Execute command on remote platform
    cmd = f"sudo -s sudo -l -U {user}"
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


# @pytest.mark.security_id(172)
def _users_home(client, user):
    # Home must be not on nfs
    # need to check if /home is a mount point
    # if it's a mount point check that's is not nfsv3 or nfsv4
    command = f"cat /etc/mtab"
    (exit_code, output, error) = client.execute_command(command, quiet=True)
    mtab =  _parse_fstab(output)
    # This will not detect when we have /home/nfs_mount.
    if '/home' in mtab.keys():
        if 'nfs' in mtab['/home']['fs']:
            nfs_version = filter(lambda x: 'vers' in x, mtab['/home']['opts'])[0]
            assert 4.0 < float(nfs_version.split("=")[1]), "Invaild NFS version"
            
    # Ownerships is of the users one and no one else
    # Default vaule should be 755. Technically, we could have
    # different permissions too, but that seems unreasoable.
    command = f"stat --format %U /home/{user}"
    (exit_code, output, error) = client.execute_command(command, quiet=True)
    assert output.split("\n")[0] == user, f"/home/{user} is not owned by the User!"

    home_perm =  get_file_perm(client, f"/home/{user}")
    postix1e = list(map(int, str(home_perm)))
    owner = postix1e[0]
    group = postix1e[1]
    world = postix1e[2]
    assert owner == 7, f"/home/{user} has the wrong permssions for owner, needs to be u+rwx"
    assert group <= 5, f"/home/{user} has the wrong permssions for group, needs to remove write permissions g+r-x or write and execute permission g+r--"
    assert world <= 5, f"/home/{user} has the wrong permssions for world, needs to remove write permissions o+r-x or write and execute permission o+r--"

    # /home/user -> User:User
    # /home/user -> 
    # Check for the ownership of all dot files.
    command = f"find /home/{user} -name \".[^.]*\""
    (exit_code, output, error) = client.execute_command(command, quiet=True)

    dot_files = output.split("\n")
    dot_files.remove("")
    for dot_file in dot_files:
      command = f"stat --format %U {dot_file}"
      (exit_code, output, error) = client.execute_command(command, quiet=True)
      assert output.split("\n")[0] == user, f"{dot_file} is not owned by the User!"
      file_perm = get_file_perm(client, dot_file)
      postix1e = list(map(int, str(file_perm)))
      owner = postix1e[0]
      group = postix1e[1]
      world = postix1e[2]
      assert owner >= 6, f"{dot_file} has the wrong permssions for owner, needs to be u+rw-"
      assert group <= 5, f"{dot_file} has the wrong permssions for group, needs to remove wirte permissions g+r--"
      assert world <= 5, f"{dot_file} has the wrong permssions for world, needs to remove write permissions o+r--"
      

      


    # No .netrc, .rhost, .forward.
    blacklisted_files = ['.netrc', '.rhost', '.forward']
    for file in blacklisted_files:
      assert False == check_file(client, file), "blacklisted file found!"
    # Check for ACLs
