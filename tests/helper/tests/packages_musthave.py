from helper.utils import get_package_list
from helper.utils import get_architecture
import os
import string
import pytest
import subprocess

def packages_musthave(client, testconfig):
    """"Test if the packages defined in pkg.include are installed"""
    installed_package_list = get_package_list(client)

    current = (os.getenv('PYTEST_CURRENT_TEST')).split('/')[0]
    path = f"/gardenlinux/features/{current}/pkg.include"
    try:
        with open(path) as f:
            packages = f.read()
    except OSError:
        pytest.skip(f"feature {current} does not have a pkg.include file")

    # collect excluded packages from all enabled features
    features = testconfig["features"]
    exclude = []
    for feature in features:
        path = f"/gardenlinux/features/{feature}/pkg.exclude"
        try:
            with open(path) as f:
                for package in f:
                    package = package.strip(string.whitespace)
                    # Skip comment lines
                    if package.startswith("#"):
                        continue
                    exclude.append(package)
        except OSError:
            continue

    # collect packages that should be ignored by the test
    # e.g. because they got excluded by later features
    ignore = []
    for feature in features:
        path = f"/gardenlinux/features/{feature}/test/pkg.ignore"
        try:
            with open(path) as f:
                for package in f:
                    package = package.strip(string.whitespace)
                    # Skip comment lines
                    if package.startswith("#"):
                        continue
                    ignore.append(package)
        except OSError:
            continue

    arch = get_architecture(client)

    missing = []
    for package in packages.splitlines():
        package = subprocess.Popen(f'set -eufo pipefail; cd "$(mktemp -d)"; arch="{arch}"; PATH=""; set -r; read line; eval "echo $line"', shell=True, executable="/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate(input=package.encode("utf-8"))[0].decode("utf-8")
        package = package.strip(string.whitespace)
        if package == "":
            continue

        # explicitly excluded packages are allowed to miss
        if package in exclude:
            continue

        # packages that should be ignored should be ignored
        if package in ignore:
            continue

        if not (package in installed_package_list or
                f"{package}:{arch}" in installed_package_list):
            missing.append(package)

    assert len(missing) == 0, \
            f"{', '.join(missing)} should be installed, but are missing"
