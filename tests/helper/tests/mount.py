import uuid
import os
import pytest
from helper.utils import execute_remote_command


def mount(client, mount_point, opt, test_type, test_val):
    """ Testing options on defined mount points """
    fstab_file = execute_remote_command(client, "cat /etc/fstab")
    fstab = _parse_fstab(fstab_file)

    # Run desired test types

    # Test for defined options
    if test_type == "opt_in_option":
        opt_in_option(client, mount_point, opt, fstab, test_val)


def opt_in_option(client, mount_point, opt, fstab, test_val):
    """ Validate if a specific option is present """
    assert mount_point in fstab, f"Could not find mount {mount_point} in /etc/fstab."
    assert opt in fstab[mount_point]["opts"], f"Could not find option {opt} for mount {mount_point} in /etc/fstab."

    # Validate the expected state by performing test(s)
    if test_val:
        _write_file(client, mount_point, fail=True)


def _write_file(client, mount_point, fail):
    """ Writes a random file on a specific mount """
    file_name = uuid.uuid4()
    rc, out = execute_remote_command(client, f"touch {mount_point}/{file_name}", skip_error=fail)
    if fail:
        assert rc == 1, f"Could write on mount {mount_point}."
    else:
        assert rc == 0, f"Could not write on mount {mount_point}."


def _parse_fstab(fstab_file):
    """ Parse a fstab file line for line and convert it to Py dict """
    fstab = {}
    for line in fstab_file.splitlines():
        fs_entry = line.split()
        mount = fs_entry[1]
        fstab[mount] = {} 
        fstab[mount]["device"] = fs_entry[0]
        fstab[mount]["mount"] = fs_entry[1]
        fstab[mount]["fs"] = fs_entry[2]
        # Convert comma separated options to list
        fstab[mount]["opts"] = fs_entry[3].split(",")
    return fstab
