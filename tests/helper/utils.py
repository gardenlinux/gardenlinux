import uuid
import os
import re
import string
import subprocess


def read_file_remote(client, file, remove_comments=False)-> list:
    """ Read a file from the remote file system and returns it for
        proper processing trunecated.
    """
    status, output = execute_remote_command(client, f"cat {file}", skip_error=True)
    #assert status == 0, f"Error reading {file}"
    to_return = output.split("\n")
    ## Check if we might have an emtory entry.
    if "" in to_return:
        to_return.remove("")
    if remove_comments:
        # Ensure that we only skip lines when the comment start with.
        return [line for line in output.split("\n") if line and not line.startswith("#")]
    return to_return


def get_package_list(client):
    """Return list with the installed packages.
    Needs the fixture client to connect into the image"""
    (exit_code, output, error) = client.execute_command("dpkg -l", quiet=True)
    assert exit_code == 0, f"no {error=} expected"
    pkgslist = []
    for line in output.split('\n'):
        if not line.startswith('ii'):
            continue
        pkg = line.split('  ')
        if len(pkg) > 1:
            pkgslist.append(pkg[1])
    return pkgslist


def read_test_config(features, testname, suffix = ".list", filter_comments = True):
    """Collect the configuration of a test from all enabled features.
    Needs the list of enabled features and the name of the test, the suffix is
    optional. It returns a list of the aggregated configs for a test."""
    config = []
    for feature in features:
        path = (f"/gardenlinux/features/{feature}/test/{testname}.d/" +
            f"{testname}{suffix}")
        if os.path.isfile(path):
            file = open(path, 'r')
            for line in file:
                # Skip comment lines
                if re.match(r'^ *#',line) and filter_comments:
                    continue
                # Skip empty lines
                if re.match(r'^\s*$', line):
                    continue
                config.append(line.strip('\n'))
    return config


def disabled_by(features, testname):
    """Checks is a test is explicitly disabled by a feature.
    Needs the list of enabled features and the name of the test.
    It returns a list of the features where the test is disabled."""
    disabled = []
    for feature in features:
        path = (f"/gardenlinux/features/{feature}/test/{testname}.disable")
        if os.path.isfile(path):
            disabled.append(feature)
    return disabled


class AptUpdate():
    def __new__(cls, client):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AptUpdate, cls).__new__(cls)

        (exit_code, output, error) = client.execute_command("apt-get update")
        assert exit_code == 0, f"no {error=} expected"

        return cls.instance


def get_file_perm(client, fname):
    """Return file permissions of a given file/dir in as int"""
    (exit_code, output, error) = client.execute_command(
        f"stat --format '%a' {fname}", quiet=True)
    # Make sure we do not test non existent directories
    if not "cannot statx" in error:
        return int(output)

def get_installed_kernel_versions(client):
    """Get a list of installed kernel versions using 'linux-version list'."""
    command = "linux-version list"
    (exit_code, output, error) = client.execute_command(command, quiet=True)
    if exit_code == 0 and output:
        kernel_versions = output.strip().split('\n')
        return kernel_versions
    else:
        return []

def check_kernel_module_exists_for_kernel_version(client, module_name, kernel_version):
    """ Checks if a kernel module exists for a given kernel version """
    
    for ext in ["ko", "ko.gz", "ko.xz", "ko.bz2", "ko.zst"]:
        filename = f"{module_name}.{ext}"
        command = f"find /lib/modules/{kernel_version} -type f -name {filename}"
        (exit_code, output, error) = client.execute_command(command, quiet=True)
        if exit_code == 0 and output:
            return True

    return False

def check_module_exists_in_all_kernels(client, module_name):
    """Check if a module exists for all installed kernel versions, considering all compression types."""
    kernel_versions = get_installed_kernel_versions(client)
    if not kernel_versions:
        print("No kernel versions found or unable to determine kernel versions.")
        return False

    for kernel_version in kernel_versions:
        if not check_kernel_module_exists_for_kernel_version(client, module_name, kernel_version):
            print(f"Module {module_name} not found for kernel version {kernel_version}.")
            return False  # Module not found for at least one kernel version

    return True  


def check_file(client, fname):
    """Return bool if file exists"""
    (exit_code, output, error) = client.execute_command(
        f"stat --format '%a' {fname}", quiet=True)
    if exit_code == 0:
        return True
    else:
        return False


def create_remote_tmp_dir(client):
    """Create a temporary directory on remote without Python usage"""
    tmp_random = uuid.uuid4()
    tmp_prefix = "gl-test-"
    tmp_name   = f"/tmp/{tmp_prefix}{tmp_random}"

    (exit_code, output, error) = client.execute_command(f"stat {tmp_name}", quiet=True)
    if exit_code != 0:
       (rc, output, error) = client.execute_command(f"mkdir {tmp_name}", quiet=True)
    return tmp_name


def get_architecture(client):
    """Get the architecture of the environment to test"""
    (exit_code, output, error) = client.execute_command("dpkg --print-architecture", quiet=True)
    assert exit_code == 0, f"no {error=} expected"
    return output.strip(string.whitespace)


def unset_env_var(client, env_var):
    """Unset env var on remote system"""
    (exit_code, output, error) = client.execute_command(f'sudo -u root "unset {env_var}"', quiet=True)
    return exit_code


def get_kernel_version(client):
    (exit_code, output, error) = client.execute_command(
        "uname -r", quiet=True)
    assert exit_code == 0, f"no {error=} expected"
    output = output.strip()
    return output


def wait_systemd_boot(client):
    """Wait for systemd to finish booting."""
    """If there are failed units, show their Logs."""
    systemd_status_cmd = "systemctl is-system-running --wait"
    systemd_failed_cmd = (
        "systemctl --failed --no-legend --no-pager | awk '{print $2}' | "
        "xargs -rn1 journalctl --no-pager --lines 100 -u"
    )

    # Check if systemd has finished booting
    exit_code, output, error = client.execute_command(systemd_status_cmd, quiet=False)

    if exit_code != 0:
        # Fetch logs of failed units
        failed_exit_code, failed_output, failed_error = client.execute_command(
            systemd_failed_cmd, quiet=False
        )
        logs = (
            failed_output if failed_exit_code == 0
            else f"Failed to fetch logs: {failed_error}"
        )
        # Append logs to debug message
        debug_message = (
            f"Systemd did not finish booting.\nError: {error}\nOutput: {output}\n"
            f"Failed unit logs:\n{logs}"
        )
        # Assert with detailed debug message
        assert exit_code == 0, debug_message


def validate_systemd_unit(client, systemd_unit, active=True):
    """ Validate a given systemd unit """
    cmd = f"systemctl status {systemd_unit}.service"
    (exit_code, output, error) = client.execute_command(
        cmd, quiet=True)

    assert exit_code == 0, f"systemd-unit: {systemd_unit} exited with 1."
    # Validate output lines of systemd-unit
    for line in output.splitlines():
        # This 'active' is realted to systemd's output
        if "Active:" in line:
            # This active is set by the function's header
            if active:
                assert not "dead" in line, f"systemd-unit: {systemd_unit} did not start."
            else:
                assert "condition failed" in line, f"systemd-unit: {systemd_unit} condition for architecture failed."


def execute_local_command(cmd):
    """ Run local commands in Docker container """
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    rc = p.returncode
    out = p.stdout.decode()
    return rc, out


def execute_remote_command(client, cmd, skip_error=False):
    """ Run remote command on test platform """
    (exit_code, output, error) = client.execute_command(
        cmd, quiet=True)
    if not skip_error:
        assert exit_code == 0, f"no {error=} expected"
        output = output.strip()
        return output
    else:
        output = output.strip()
        return exit_code, output


def get_installed_kernel_versions(client):
    """Get a list of installed kernel versions using 'linux-version list'."""
    command = "linux-version list"
    (exit_code, output, error) = client.execute_command(command, quiet=True)
    if exit_code == 0 and output:
        kernel_versions = output.strip().split('\n')
        return kernel_versions
    else:
        return []

def get_kernel_config_paths(client):
    kernel_versions = get_installed_kernel_versions(client)
    paths = []
    for k in kernel_versions:
        config_path = f"/boot/config-{k}"
        if check_file(client, config_path):
            paths.append(config_path)
    return paths


def install_package_deb(client, pkg):
    """ Installs (a) Debian packagei(s) on a target platform """
    # Packages for testing may not be included within the Garden Linux
    # repository. We may add a native Debian repo to the temp chroot for
    # further unit testing
    (exit_code, output, error) = client.execute_command(
        "grep 'https://cdn-aws.deb.debian.org/debian bookworm main' /etc/apt/sources.list", quiet=True)
    if exit_code > 0:
       (exit_code, output, error) = client.execute_command(
           "echo 'deb https://cdn-aws.deb.debian.org/debian bookworm main' >> /etc/apt/sources.list && apt-get update", quiet=True)
       assert exit_code == 0, f"Could not add native Debian repository."

    # Finally, install the package
    (exit_code, output, error) = client.execute_command(
        f"apt-get install -y --no-install-recommends {pkg}", quiet=True)
    assert exit_code == 0, f"Could not install Debian Package: {error}"

def check_kernel_config_exact(client, kernel_config_path, kernel_config_item):
    """ Checks if the given kernel_config_item is set in kernel_config_path """

    assert check_file(client, kernel_config_path), f"Kernel config does not exist - {kernel_config_path}"

    command = f"grep -qE '^{kernel_config_item}$' '{kernel_config_path}'"
    (exit_code, output, error) = client.execute_command(command, quiet=True)
    return exit_code == 0



