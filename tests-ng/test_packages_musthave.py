import pytest
from plugins.shell import ShellRunner
from plugins.dpkg import Dpkg
from plugins.features import features as flavor_features

import os
import string
import subprocess

def parse_pkg(feature: str, file: str, skip_on_error: bool = False) -> set[str]:
    path = f"includes/features/{feature}/{file}"
    result = set()
    try:
        with open(path) as f:
            for package in f:
                package = package.strip(string.whitespace)
                # Skip comment lines
                if package.startswith("#") or package == "":
                    continue
                result.add(package)
    except OSError:
        if skip_on_error:
            pytest.skip(f"feature {feature} does not have a {file} file")
    return result

# {feature -> [ ignored missing packages, e.g. because they got excluded by later features ]}
features = {
    "_bfpxe": [],
    "_dev": [],
    "_iso": [],
    "_pxe": [],
    "_selinux": [],
    "aide": [],
    "ali": [],
    "aws": [],
    "azure": [],
    "base": [],
    "bluefield": [],
    "chost": [],
    "clamav": [],
    "cloud": [],
    "fedramp": [],
    "firewall": [],
    "gardener": [],
    "gcp": [],
    "iscsi": [],
    "khost": [],
    "kvm": [],
    "metal": [],
    "nvme": [],
    "openstack": [],
    "openstackbaremetal": [],
    "server": ["systemd-coredump"],
    "vhost": [],
    "vmware": []
}

@pytest.mark.parametrize(
    "current,ignore", [pytest.param(feature, features[feature], marks=pytest.mark.feature(feature), id=feature) for feature in features]
)
def test_packages_musthave(shell: ShellRunner, dpkg: Dpkg, current, ignore):
    """Test if the packages defined in pkg.include are installed"""
    arch = dpkg.architecture()

    includes = parse_pkg(current, "pkg.include", skip_on_error=True)
    packages = set()
    for package in includes:
        # Some pkg.include files use the $arch variable or bash if statements, therefore this cannot be replaced by a simple pyhton function
        output = shell(f'arch="{arch}"; line="{package}"; eval "echo $line"', capture_output=True)
        package = output.stdout.strip(string.whitespace)
        print(package)
        if package != "":
            packages.add(package)


    # collect excluded packages from all enabled features
    exclude = set(ignore)
    for feature in flavor_features:
        exclude = exclude.union(parse_pkg(feature, "pkg.exclude"))

    required = packages - exclude

    

    print(packages)
    print(exclude)
    
    missing = set()
    for package in required:        
        if not dpkg.package_is_installed(package):
            missing.add(package)

    assert len(missing) == 0, \
            f"{', '.join(sorted(missing))} should be installed, but are missing"


"""

FAILED test_packages_musthave.py::test_packages_musthave[aws] - AssertionError: cloud-init, amazon-ec2-utils should be installed, but are missing
FAILED test_packages_musthave.py::test_packages_musthave[base] - AssertionError: garden-repo-manager should be installed, but are missing
FAILED test_packages_musthave.py::test_packages_musthave[cloud] - AssertionError: linux-image-cloud-$arch should be installed, but are missing
FAILED test_packages_musthave.py::test_packages_musthave[server] - AssertionError: ca-certificates, dnsutils, lsb-release, netbase, sosreport should be installed, but are missing


FAILED test_packages_musthave.py::test_packages_musthave[aws] - AssertionError: amazon-ec2-utils, cloud-init should be installed, but are missing
FAILED test_packages_musthave.py::test_packages_musthave[base] - AssertionError: garden-repo-manager should be installed, but are missing
FAILED test_packages_musthave.py::test_packages_musthave[cloud] - AssertionError: linux-image-cloud-$arch should be installed, but are missing
FAILED test_packages_musthave.py::test_packages_musthave[server] - AssertionError: ca-certificates, dnsutils, lsb-release, netbase, sosreport should be installed, but are missing


SKIPPED [1] test_packages_musthave.py:164: excluded by feature condition: _bfpxe
SKIPPED [1] test_packages_musthave.py:164: excluded by feature condition: _iso
SKIPPED [1] test_packages_musthave.py:164: excluded by feature condition: aide
SKIPPED [1] test_packages_musthave.py:164: excluded by feature condition: azure
SKIPPED [1] test_packages_musthave.py:164: excluded by feature condition: bluefield
SKIPPED [1] test_packages_musthave.py:164: excluded by feature condition: clamav
SKIPPED [1] test_packages_musthave.py:164: excluded by feature condition: fedramp
SKIPPED [1] test_packages_musthave.py:164: excluded by feature condition: openstack
SKIPPED [1] test_packages_musthave.py:164: excluded by feature condition: openstackbaremetal
SKIPPED [1] test_packages_musthave.py:164: excluded by feature condition: vmware


aws
PASSED test_packages_musthave.py::test_packages_musthave[aws]
PASSED test_packages_musthave.py::test_packages_musthave[base]
PASSED test_packages_musthave.py::test_packages_musthave[cloud]
PASSED test_packages_musthave.py::test_packages_musthave[gardener]
PASSED test_packages_musthave.py::test_packages_musthave[iscsi]
PASSED test_packages_musthave.py::test_packages_musthave[nvme]
PASSED test_packages_musthave.py::test_packages_musthave[server]

metal-capi-arm64
PASSED test_packages_musthave.py::test_packages_musthave[_pxe]
PASSED test_packages_musthave.py::test_packages_musthave[base]
PASSED test_packages_musthave.py::test_packages_musthave[chost]
PASSED test_packages_musthave.py::test_packages_musthave[khost]
PASSED test_packages_musthave.py::test_packages_musthave[metal]
PASSED test_packages_musthave.py::test_packages_musthave[server]

metal-vhost-arm64
PASSED test_packages_musthave.py::test_packages_musthave[_selinux]
PASSED test_packages_musthave.py::test_packages_musthave[base]
PASSED test_packages_musthave.py::test_packages_musthave[firewall]
PASSED test_packages_musthave.py::test_packages_musthave[metal]
PASSED test_packages_musthave.py::test_packages_musthave[server]

kvm-vhost_dev-arm64
PASSED test_packages_musthave.py::test_packages_musthave[_dev]
PASSED test_packages_musthave.py::test_packages_musthave[_selinux]
PASSED test_packages_musthave.py::test_packages_musthave[base]
PASSED test_packages_musthave.py::test_packages_musthave[cloud]
PASSED test_packages_musthave.py::test_packages_musthave[firewall]
PASSED test_packages_musthave.py::test_packages_musthave[kvm]
PASSED test_packages_musthave.py::test_packages_musthave[server]
PASSED test_packages_musthave.py::test_packages_musthave[vhost]

gcp-gardener_prod-arm64
PASSED test_packages_musthave.py::test_packages_musthave[base]
PASSED test_packages_musthave.py::test_packages_musthave[cloud]
PASSED test_packages_musthave.py::test_packages_musthave[gardener]
PASSED test_packages_musthave.py::test_packages_musthave[gcp]
PASSED test_packages_musthave.py::test_packages_musthave[iscsi]
PASSED test_packages_musthave.py::test_packages_musthave[nvme]
PASSED test_packages_musthave.py::test_packages_musthave[server]

PASSED test_packages_musthave.py::test_packages_musthave[ali]
PASSED test_packages_musthave.py::test_packages_musthave[base]
PASSED test_packages_musthave.py::test_packages_musthave[cloud]
PASSED test_packages_musthave.py::test_packages_musthave[gardener]
PASSED test_packages_musthave.py::test_packages_musthave[iscsi]
PASSED test_packages_musthave.py::test_packages_musthave[nvme]
PASSED test_packages_musthave.py::test_packages_musthave[server]
"""