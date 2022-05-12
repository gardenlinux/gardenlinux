from helper.utils import get_package_list
from helper.utils import get_architecture
import os
import string
import pytest

def packages_musthave(client):
    """"Test if the packages defined in pkg.include are installed"""
    installed_pkgslist = get_package_list(client)

    current = (os.getenv('PYTEST_CURRENT_TEST')).split('/')[0]
    path = f"/gardenlinux/features/{current}/pkg.include"
    try:
        with open(path) as f:
            packages = f.read()
    except OSError:
        pytest.skip(f"feature {current} does not have a pkg.include file")

    arch = get_architecture(client)

    missing = []
    for package in packages.splitlines():
        package = package.strip(string.whitespace)
        # ignore comments
        if package.startswith("#"):
            continue
        # normalize package name if the line in pkg.include contains:
        # * the architecture as condition
        elif package.startswith(r"[${arch}"):
            if arch in package:
                package = package.split(" ")[-1]
            else:
                continue
        # * an url to the package
        elif package.startswith("http"):
            package_name = package.split("/")[-1]
            package = package_name.split("_")[0]
        # * the architecture as a variable in the package name
        elif package.endswith(r"-${arch}"):
            package = package.replace(r"${arch}", arch)

        if not (package in installed_pkgslist or
                f"{package}:{arch}" in installed_pkgslist):
            missing.append(package)

    assert len(missing) == 0, \
            f"{', '.join(missing)} should be installed, but are missing"