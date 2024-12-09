import pytest
from helper.utils import execute_remote_command, read_file_remote

@pytest.mark.secrutiy_id(321)
def test_pam(client):
    """
        This checks that the pre-requiements are set to operate with
        a OpenLDAP backend. Note this will *not* installed libpam-ldap
        or check for it.
    """
    file_list = [ "common-session", 
                  "common-password", 
                  "common-auth", 
                  "common-account", 
                  "login", "su", 
                  "sudo", "sshd" 
                 ]
 

    for file in file_list:
       content = read_file_remote(client, f"/etc/pam.d/{file}")
       assert len(content) != 0, f"Problem reading /etc/pam.d/{file}. Missing packages from libpam?"

    
    package_list = [ "libpam-runtime", "libpam-systemd", "libpam-passwdqc", "libpam-modules", "libpam-modules-bin"]
    for libpam_package in package_list:
        output = execute_remote_command(client, f"dpkg -l {libpam_package}")
        # When the package is failing, we will get an error form execute_remote_command.
        assert len(content) != 0








