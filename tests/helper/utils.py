import os
import re

def get_package_list(client):
    """Return list with the installed packages.
    Needs the fixture client to connect into the image"""
    (exit_code, output, error) = client.execute_command("dpkg -l")
    assert exit_code == 0, f"no {error=} expected"
    pkgslist = []
    for line in output.split('\n'):
        if not line.startswith('ii'):
            continue
        pkg = line.split('  ')
        if len(pkg) > 1:
            pkgslist.append(pkg[1])
    return pkgslist


def read_test_config(features, testname, suffix = ".list"):
    """Collect the configuration of a test from all enabled features.
    Needs the list of enabled features and the name of the test, the suffix is optional.
    It returns a list of the aggregated configs for a test."""
    config = []
    for feature in features:
        path = ("/gardenlinux/features/%s/test/%s.d/%s%s" % (feature, testname, testname, suffix))
        if os.path.isfile(path):
            file = open(path, 'r')
            for line in file:
                if line.startswith('#'):
                    continue
                if re.match(r'^\s*$', line):
                    continue
                config.append(line.strip('\n'))
    return config


def is_disabled(features, testname):
    """Checks is a test is explicitly disabled by a feature.
    Needs the list of enabled features and the name of the test.
    It returns a list of the features where the test is disabled."""
    disabled = []
    for feature in features:
        path = ("/gardenlinux/features/%s/test/%s.disable" % (feature, testname))
        if os.path.isfile(path):
            disabled.append(feature)
    return disabled


class AptUpdate():
    def __new__(cls, client):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AptUpdate, cls).__new__(cls)

        (exit_code, output, error) = client.execute_command("apt-get update")
        assert exit_code == 0, f"no {error=} expected"