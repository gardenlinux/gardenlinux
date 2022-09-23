from helper.utils import get_package_list
from helper.utils import get_architecture
import os
import string
import pytest

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
        elif package.endswith(r".deb"):
            package_name = os.path.basename(package)
            package = package_name.split("_")[0]
        # * the architecture as a variable in the package name
        elif package.endswith(r"-${arch}"):
            package = package.replace(r"${arch}", arch)

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