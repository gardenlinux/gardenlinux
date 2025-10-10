import pytest
import json
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Package:
    """Represents an installed package"""
    package: str
    version: str
    status: str = ""
    priority: str = ""
    section: str = ""
    installed_size: str = ""
    maintainer: str = ""
    architecture: str = ""
    multi_arch: str = ""
    source: str = ""
    provides: str = ""
    depends: str = ""
    breaks: str = ""
    conflicts: str = ""
    description: str = ""
    homepage: str = ""
    suggests: str = ""
    recommends: str = ""
    replaces: str = ""
    pre_depends: str = ""
    essential: str = ""

    def __str__(self) -> str:
        return f"{self.package}\t{self.version}"


@dataclass
class InstalledPackages:
    """Collection of installed packages"""
    packages: List[Package]

    def __len__(self) -> int:
        return len(self.packages)

    def __iter__(self):
        return iter(self.packages)

    def __getitem__(self, key):
        return self.packages[key]

    def get_package(self, name: str):
        """Get package by name"""
        return next((p for p in self.packages if p.package == name), None)


class Dpkg:
    def __init__(self, shell=None):
        pass

    def collect_installed_packages(self) -> InstalledPackages:
        """Convert /var/lib/dpkg/status to JSON and return installed packages"""
        try:
            with open("/var/lib/dpkg/status", "r", encoding="utf-8") as f:
                content = f.read()
        except (FileNotFoundError, PermissionError):
            return InstalledPackages([])

        packages = []
        current_package = {}

        def add_package():
            if current_package.get('Status', '').startswith('install ok installed'):
                packages.append(Package(
                    package=current_package.get('Package', ''),
                    version=current_package.get('Version', ''),
                    status=current_package.get('Status', ''),
                    priority=current_package.get('Priority', ''),
                    section=current_package.get('Section', ''),
                    installed_size=current_package.get('Installed-Size', ''),
                    maintainer=current_package.get('Maintainer', ''),
                    architecture=current_package.get('Architecture', ''),
                    multi_arch=current_package.get('Multi-Arch', ''),
                    source=current_package.get('Source', ''),
                    provides=current_package.get('Provides', ''),
                    depends=current_package.get('Depends', ''),
                    breaks=current_package.get('Breaks', ''),
                    conflicts=current_package.get('Conflicts', ''),
                    description=current_package.get('Description', ''),
                    homepage=current_package.get('Homepage', ''),
                    suggests=current_package.get('Suggests', ''),
                    recommends=current_package.get('Recommends', ''),
                    replaces=current_package.get('Replaces', ''),
                    pre_depends=current_package.get('Pre-Depends', ''),
                    essential=current_package.get('Essential', ''),
                ))

        for line in content.split('\n'):
            if line.strip() == "":
                add_package()
                current_package = {}
            elif ':' in line:
                key, value = line.split(':', 1)
                current_package[key.strip()] = value.strip()

        add_package()  # Handle last package
        packages.sort(key=lambda p: p.package)
        return InstalledPackages(packages)

    def package_is_installed(self, package: str) -> bool:
        """Check if package is installed"""
        return self.collect_installed_packages().get_package(package) is not None

    def architecture_native(self) -> str:
        """Get the native architecture of the system"""
        with open('/var/lib/dpkg/arch-native') as f:
            return f.read().strip()

    def architectures_foreign(self) -> list[str]:
        """Get the foreign architectures of the system"""
        with open('/var/lib/dpkg/arch') as f:
            native = self.architecture_native()
            return list(filter(lambda x: x != native, f.read().split('\n')))

    def architectures(self) -> list[str]:
        """Get the native and foreign architectures of the system"""
        with open('/var/lib/dpkg/arch') as f:
            return list(filter(None, f.read().split('\n')))


@pytest.fixture
def dpkg(shell=None) -> Dpkg:
    return Dpkg(shell)
