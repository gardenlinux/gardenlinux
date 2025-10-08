import pytest
from plugins.shell import ShellRunner
from plugins.dpkg import Dpkg
from plugins.features import features as flavor_features

def parse_pkg(feature: str, file: str, skip_on_error: bool = False) -> set[str]:
    path = f"includes/features/{feature}/{file}"
    result = set()
    try:
        with open(path) as f:
            for package in f:
                package = package.strip()
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
        package = output.stdout.strip()
        if package != "":
            packages.add(package)


    # collect excluded packages from all enabled features
    exclude = set(ignore)
    for feature in flavor_features:
        exclude = exclude.union(parse_pkg(feature, "pkg.exclude"))

    required = packages - exclude
    
    missing = set()
    for package in required:        
        if not dpkg.package_is_installed(package):
            missing.add(package)

    assert len(missing) == 0, \
            f"{', '.join(sorted(missing))} should be installed, but are missing"
