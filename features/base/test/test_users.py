from helper.tests.users import users
from helper.utils import check_file, get_file_perm
from helper.test.mount import _parse_fstab
import pytest



@pytest.mark.security_id(172)
def test_users_home(client, username):
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
            assert 4.0 < float(nfs_version.split("=")[1])
            
    # Ownerships is of the users one and no one else
    # Default vaule should be 755. Technically, we could have
    # different permissions too, but that seems unreasoable.
    home_perm =  get_file_perm(f"/home/{username}")
    assert home_perm, 755 

    # /home/user -> User:User
    # /home/user -> 
    # Check for the ownership of all dot files.
    command = f"find /home/{username} -name \".[^.]*\""
    (exit_code, output, error) = client.execute_command(command, quiet=True)
    # No .netrc, .rhost, forward.
    for file in backlisted_files:
      assert False check_file(file) 
    # Check for ACLs




@pytest.mark.security_id(164)
def test_for_root(client):

     (exit_code, output, error) = client.execute_command( "getent passwd", quiet=True)
     assert exit_code == 0, f"no {error=} expected"

     # Remove the empty newline for simple looping.
     passwd = output.split("\n")
     passwd.remove("")

     # passwd format, we only care for the frist and third entry.
     # 0. login name
     # 1. optional encrypted password
     # 2. numerical user ID
     # 3. numerical group ID
     # 4. user name or comment field
     # 5. user home directory
     # 6. optional user command interpreter

     login_name = 0
     numeric_user_id = 2

     # test if we have only a single user with root and id 0.
     entries_with_root_name = [entry for entry in passwd if 'root' in
                               entry.split(":")[login_name]]
     entries_with_root_id   = [entry for entry in passwd if '0' ==
                               entry.split(":")[numeric_user_id]]
     assert len(entries_with_root_name), 1
     assert len(entries_with_root_id), 1


@pytest.mark.security_id(179)
def test_users(client, non_dev, non_feature_githubActionRunner, non_vhost, non_hyperscalers, non_container, non_ccee):
     users(client)
