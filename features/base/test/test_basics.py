import pytest
from helper.utils import get_architecture, AptUpdate, install_package_deb, execute_remote_command, read_file_remote
from helper.sshclient import RemoteClient


@pytest.mark.security_id(1)
def test_gl_is_support_distro(client):
    """Test that gardenlinux is a support vendor. """

    AptUpdate(client)
    install_package_deb(client, "dpkg-dev")
    assert '' ==  execute_remote_command(client, "dpkg-vendor --is gardenlinux")
    assert '' ==  execute_remote_command(client, "dpkg-vendor  --derives-from debian")

    # Negative case:
    status, output  = execute_remote_command(client, "dpkg-vendor --is debian", skip_error=True)
    assert status == 1


@pytest.mark.security_id(483)
def test_that_PATH_was_set(client):
    """
       Ensure that we have valide $PATH variable present.
    """
    bash_env = execute_remote_command(client, "env")
    PATH = [n for n in bash_env.split("\n") if 'PATH' in n]
    assert len(PATH) == 1, "Can't find PATH"
    assert "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" == PATH[0], "PATH is not set correctly."

    # Validate the we use PATH that are only located in the default part of the FHS.
    entries = PATH[0].split("=")[1].split(":")
    # trustworthy path
    # /usr
    # /usr/local
    # /sbin
    # /bin
    # path_suffix = sbin / bin
    from pathlib import Path
    for path_entry in entries:
        _path_obj = Path(path_entry)
        assert _path_obj.root == "/", "PATH entry was detect that's located not on root."
        assert _path_obj.is_absolute(), "Not an absolute path." 

@pytest.mark.security_id(485)
def test_bash_timeout_was_set(client, non_container):
    """
       Check that we have set the necessary timeout by default to 900.
    """
    autologout = read_file_remote(client,  "/etc/profile.d/50-autologout.sh", remove_comments=True)
    assert ['TMOUT=900', 'readonly TMOUT', 'export TMOUT'] == autologout, "Timeout missing for bash"


def test_no_man(client):
    """ Test that no man files are present """
    (exit_code, _, error) = client.execute_command("man ls", disable_sudo=True)
    assert exit_code == 127, '"man" should not be installed'
    assert "man: command not found" in error


def test_ls(client):
    """ Test for regular linux folders/mounts """
    (exit_code, output, error) = client.execute_command("ls /")
    assert exit_code == 0, f"no {error=} expected"
    assert output
    arch = get_architecture(client)
    lines = output.split("\n")
    assert "bin" in lines
    assert "boot" in lines
    assert "dev" in lines
    assert "etc" in lines
    assert "home" in lines
    assert "lib" in lines
    if arch == "amd64":
        assert "lib64" in lines
    assert "mnt" in lines
    assert "opt" in lines
    assert "proc" in lines
    assert "root" in lines
    assert "run" in lines
    assert "sbin" in lines
    assert "srv" in lines
    assert "sys" in lines
    assert "tmp" in lines
    assert "usr" in lines
    assert "var" in lines


def test_startup_time(client, non_chroot, non_kvm, non_azure):
    """ Test for startup time """
    tolerated_kernel_time = 30
    tolerated_userspace_time = 40
    (exit_code, output, error) = client.execute_command("systemd-analyze")
    assert exit_code == 0, f"no {error=} expected"
    lines = output.splitlines()
    items = lines[0].split(" ")
    time_initrd = 0
    for i, v in enumerate(items):
        if v == "(kernel)":
            time_kernel = items[i-1]
        if v == "(initrd)":
            time_initrd = items[i-1]
        if v == "(userspace)":
            time_userspace = items[i-1]
    if len(time_kernel) >2 and time_kernel[-2:] == "ms":
        time_kernel = str(float(time_kernel[:-2]) / 1000.0) + "s"
    if len(time_initrd) >2 and time_initrd[-2:] == "ms":
        time_initrd = str(float(time_initrd[:-2]) / 1000.0) + "s"
    tf_kernel = float(time_kernel[:-1]) + float(time_initrd[:-1])
    tf_userspace = float(time_userspace[:-1])
    assert tf_kernel < tolerated_kernel_time, f"startup time in kernel space too long: {tf_kernel} seconds =  but only {tolerated_kernel_time} tolerated."
    assert tf_userspace < tolerated_userspace_time, f"startup time in user space too long: {tf_userspace}seconds but only {tolerated_userspace_time} tolerated."


def test_startup_script(client, gcp):
    """ Test for validity of startup script on gcp """
    (exit_code, output, error) = client.execute_command("test -f /tmp/startup-script-ok")
    assert exit_code == 0, f"no {error=} expected. Startup script did not run"
