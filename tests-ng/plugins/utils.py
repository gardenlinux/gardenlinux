
import uuid
import os
import re
import string
import subprocess
from pathlib import Path
from typing import Iterable, List, Dict, Optional

import pytest


def parse_etc_file(
    path: Path,
    *,
    field_names: Optional[Iterable[str]] = None,
    min_fields: int = 1,
    sep: str = ":",
    skip_comments: bool = True,
    strip_whitespace: bool = True,
) -> List[Dict[str, str | List[str]]]:
    """
    Generic parser for /etc/* style files (passwd, shadow, group, etc.).

    - path: Path to the file (e.g., Path('/etc/passwd'))
    - field_names: optional iterable of names to assign to fields.
        * If provided and fewer than the number of fields on a line,
          all remaining fields are collected into the **last** name as a list.
        * If more names than fields exist on a line, the missing ones are set to ''.
    - min_fields: assert each non-empty, non-comment line has at least this many fields.
    - sep: field separator (default ':').

    Returns: list of dicts; values are str, except the last named field may be List[str]
             when there are extra trailing fields.
    """
    assert path.is_file(), f"File not found: {path}"
    text = path.read_text(encoding="utf-8", errors="ignore")

    names: List[str] = list(field_names) if field_names else []
    out: List[Dict[str, str | List[str]]] = []

    for raw in text.splitlines():
        line = raw.strip() if strip_whitespace else raw
        if not line:
            continue
        if skip_comments and line.startswith("#"):
            continue

        parts = line.split(sep)
        assert len(parts) >= min_fields, (
            f"Malformed line in {path}: expected >= {min_fields} fields, got {len(parts)}\n"
            f"Line: {raw!r}"
        )

        if not names:
            # No names supplied: return numbered fields as strings f0, f1, ...
            entry = {f"f{i}": v for i, v in enumerate(parts)}
            out.append(entry)
            continue

        # Names supplied:
        if len(names) == 1:
            # Single name -> capture all fields into a list
            out.append({names[0]: parts})
            continue

        head_names = names[:-1]
        tail_name = names[-1]

        entry: Dict[str, str | List[str]] = {}
        # Map head 1:1 (missing -> '')
        for i, n in enumerate(head_names):
            entry[n] = parts[i] if i < len(parts) else ""

        # Tail collects the rest (may be one or many)
        rest = parts[len(head_names):]
        # If there is exactly one remainder, store as str for convenience;
        # if multiple, store as list.
        if len(rest) <= 1:
            entry[tail_name] = rest[0] if rest else ""
        else:
            entry[tail_name] = rest

        out.append(entry)

    return out


def read_file_remote(client, file, remove_comments=False, remove_newlines=False) -> list:
    """Read a file from the remote file system and return its lines for further processing."""
    status, output = execute_remote_command(client, f"cat {file}", skip_error=True)
    assert status == 0, f"Error reading {file}"
    to_return = []
    for line in output.split("\n"):
        # Skip empty entries when requested
        if remove_newlines and not line:
            continue
        # Skip comment lines only if they start with '#'
        if remove_comments and line.startswith('#'):
            continue
        to_return.append(line)
    return to_return


def get_package_list(client):
    """Return a list with the installed packages (requires Debian dpkg)."""
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


def read_test_config(features, testname, suffix=".list", filter_comments=True):
    """
    Collect the configuration of a test from all enabled features.
    Returns a list of aggregated config lines for the given test.
    """
    config = []
    for feature in features:
        path = (
            f"/gardenlinux/features/{feature}/test/{testname}.d/"
            f"{testname}{suffix}"
        )
        if os.path.isfile(path):
            with open(path, 'r') as file:
                for line in file:
                    # Skip comment lines
                    if re.match(r'^ *#', line) and filter_comments:
                        continue
                    # Skip empty lines
                    if re.match(r'^\s*$', line):
                        continue
                    config.append(line.strip('\n'))
    return config


def disabled_by(features, testname):
    """
    Check if a test is explicitly disabled by a feature.
    Returns a list of features where the test is disabled.
    """
    disabled = []
    for feature in features:
        path = f"/gardenlinux/features/{feature}/test/{testname}.disable"
        if os.path.isfile(path):
            disabled.append(feature)
    return disabled


class AptUpdate:
    def __new__(cls, client):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AptUpdate, cls).__new__(cls)
        (exit_code, output, error) = client.execute_command("apt-get update", sudo=True)
        assert exit_code == 0, f"no {error=} expected"
        return cls.instance


def get_file_perm(client, fname):
    """Return file permissions of a given file/dir as int, or None if not found."""
    (exit_code, output, error) = client.execute_command(
        f"stat --format '%a' {fname}", quiet=True
    )
    # Make sure we do not test non-existent directories
    if "cannot statx" not in error:
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
    """Check if a kernel module exists for a given kernel version (considers common compressions)."""
    for ext in ["ko", "ko.gz", "ko.xz", "ko.bz2", "ko.zst"]:
        filename = f"{module_name}.{ext}"
        command = f"find /lib/modules/{kernel_version} -type f -name {filename}"
        (exit_code, output, error) = client.execute_command(command, quiet=True)
        if exit_code == 0 and output:
            return True
    return False


def check_module_exists_in_all_kernels(client, module_name):
    """
    Check if a module exists for all installed kernel versions, considering all compression types.
    Uses prints for diagnostics to keep behavior consistent with the sample.
    """
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
    """Return True if file exists, False otherwise."""
    (exit_code, output, error) = client.execute_command(
        f"stat --format '%a' {fname}", quiet=True
    )
    return exit_code == 0


def create_remote_tmp_dir(client):
    """Create a temporary directory on remote without Python usage."""
    tmp_random = uuid.uuid4()
    tmp_prefix = "gl-test-"
    tmp_name = f"/tmp/{tmp_prefix}{tmp_random}"

    (exit_code, output, error) = client.execute_command(f"stat {tmp_name}", quiet=True)
    if exit_code != 0:
        (rc, output, error) = client.execute_command(f"mkdir {tmp_name}", quiet=True)
    return tmp_name


def get_architecture(client):
    """Get the architecture of the environment to test."""
    (exit_code, output, error) = client.execute_command("dpkg --print-architecture", quiet=True)
    assert exit_code == 0, f"no {error=} expected"
    return output.strip(string.whitespace)


def unset_env_var(client, env_var):
    """Unset env var on remote system."""
    (exit_code, output, error) = client.execute_command(
        f'sudo -u root "unset {env_var}"', quiet=True
    )
    return exit_code


def get_kernel_version(client):
    """Return the current running kernel version (uname -r)."""
    (exit_code, output, error) = client.execute_command("uname -r", quiet=True)
    assert exit_code == 0, f"no {error=} expected"
    return output.strip()


def wait_systemd_boot(client):
    """
    Wait for systemd to finish booting.
    If there are failed units, show their logs and fail with a detailed message.
    """
    systemd_status_cmd = "systemctl is-system-running --wait"
    systemd_failed_cmd = (
        "systemctl --failed --no-legend --no-pager | awk '{print $2}' | "
        "xargs -rn1 journalctl --no-pager --lines 100 -u"
    )

    exit_code, output, error = client.execute_command(systemd_status_cmd, quiet=False)

    if exit_code != 0:
        failed_exit_code, failed_output, failed_error = client.execute_command(
            systemd_failed_cmd, quiet=False
        )
        logs = (
            failed_output if failed_exit_code == 0
            else f"Failed to fetch logs: {failed_error}"
        )
        debug_message = (
            f"Systemd did not finish booting.\nError: {error}\nOutput: {output}\n"
            f"Failed unit logs:\n{logs}"
        )
        assert exit_code == 0, debug_message


def validate_systemd_unit(client, systemd_unit, active=True):
    """Validate a given systemd unit by checking its 'Active:' line from systemctl status."""
    cmd = f"systemctl status {systemd_unit}.service"
    (exit_code, output, error) = client.execute_command(cmd, quiet=True)
    assert exit_code == 0, f"systemd-unit: {systemd_unit} exited with 1."
    for line in output.splitlines():
        # This 'active' is related to systemd's output
        if "Active:" in line:
            if active:
                assert "dead" not in line, f"systemd-unit: {systemd_unit} did not start."
            else:
                assert "condition failed" in line, (
                    f"systemd-unit: {systemd_unit} condition for architecture failed."
                )


def execute_local_command(cmd):
    """Run a local command in the Docker/containerized test environment."""
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    rc = p.returncode
    out = p.stdout.decode()
    return rc, out


def execute_remote_command(client, cmd, skip_error=False, sudo=False):
    """
    Run a remote command on the test platform.
    - If skip_error=False (default): asserts exit_code==0 and returns 'output' (str).
    - If skip_error=True: returns (exit_code, output) without asserting.
    - If sudo=True: run with sudo/su fallback if not already root.
    """
    if sudo:
        cmd = (
            "if [ $(id -u) = 0 ]; then {cmd}; "
            "elif [ $(which sudo) ]; then sudo /bin/bash -c '{safe}'; "
            "else su -l -c '{safe}'; fi"
        ).format(
            cmd=cmd,
            safe=cmd.replace("'", "'\"'\"'")
        )
    (exit_code, output, error) = client.execute_command(cmd, quiet=True)
    output = output.strip()
    if not skip_error:
        assert exit_code == 0, f"no {error=} expected"
        return output
    else:
        return exit_code, output


def get_kernel_config_paths(client):
    """Return list of /boot/config-* files corresponding to installed kernel versions."""
    kernel_versions = get_installed_kernel_versions(client)
    paths = []
    for k in kernel_versions:
        config_path = f"/boot/config-{k}"
        if check_file(client, config_path):
            paths.append(config_path)
    return paths


def install_package_deb(client, pkg):
    """Install Debian package(s) on the target platform (adds Debian repo if missing)."""
    (exit_code, output, error) = client.execute_command(
        "grep 'https://cdn-aws.deb.debian.org/debian bookworm main' /etc/apt/sources.list",
        quiet=True,
        sudo=True
    )
    if exit_code > 0:
        (exit_code, output, error) = client.execute_command(
            "echo 'deb https://cdn-aws.deb.debian.org/debian bookworm main' >> /etc/apt/sources.list && apt-get update",
            quiet=True,
            sudo=True
        )
        assert exit_code == 0, "Could not add native Debian repository."

    (exit_code, output, error) = client.execute_command(
        f"apt-get install -y --no-install-recommends {pkg}",
        quiet=True,
        sudo=True
    )
    assert exit_code == 0, f"Could not install Debian Package: {error}"


def check_kernel_config_exact(client, kernel_config_path, kernel_config_item):
    """Check if the given kernel_config_item is set exactly in kernel_config_path."""
    assert check_file(client, kernel_config_path), (
        f"Kernel config does not exist - {kernel_config_path}"
    )
    command = f"grep -qE '^{kernel_config_item}$' '{kernel_config_path}'"
    (exit_code, output, error) = client.execute_command(command, quiet=True)
    return exit_code == 0

# --- Already present above ---
# from ..helper.utils import execute_remote_command
# def parse_etc_file(...)

def equals_ignore_case(a: str, b: str) -> bool:
    """Return True if both strings are equal ignoring case, else False."""
    return a.lower() == b.lower()

def get_normalized_sets(iterable):
    """
    Normalize any iterable into a Python set of lowercase strings.
    Example: ['SSH', 'ssh ', ' SSh'] -> {'ssh'}
    """
    return {str(x).strip().lower() for x in iterable}

def is_set(value) -> bool:
    """Return True if the given value is a Python set."""
    return isinstance(value, set)

