import uuid
import os
import re
import string


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


def create_remote_tmp_dir(client):
    """Create a temporary directory on remote without Python usage"""
    tmp_random = uuid.uuid4()
    tmp_prefix = "gl-test-"
    tmp_name   = f"/tmp/{tmp_prefix}{tmp_random}"

    (exit_code, output, error) = client.execute_command(f"stat {tmp_name}", quiet=True)
    if exit_code is not 0:
       (rc, output, error) = client.execute_command(f"mkdir {tmp_name}", quiet=True)
    return tmp_name


def get_architecture(client):
    """Get the architecture of the environment to test"""
    (exit_code, output, error) = client.execute_command("dpkg --print-architecture", quiet=True)
    assert exit_code == 0, f"no {error=} expected"
    return output.strip(string.whitespace)