import json
from dataclasses import dataclass, field
from typing import Dict, List

import pytest
from debian import deb822

from .shell import ShellRunner


class InstalledPackages:
    """Collection of installed packages using deb822 paragraphs"""

    packages: List[deb822.Deb822]

    def __init__(self, packages: List[deb822.Deb822]):
        self.packages = packages

    def __len__(self) -> int:
        return len(self.packages)

    def __iter__(self):
        return iter(self.packages)

    def __getitem__(self, key):
        return self.packages[key]

    def get_package(self, name: str):
        """Get package by name"""
        return next((p for p in self.packages if p.get("Package") == name), None)


class Dpkg:
    def __init__(self, shell=None):
        pass

    def collect_installed_packages(self) -> InstalledPackages:
        """Use deb822 to return installed packages"""
        try:
            with open("/var/lib/dpkg/status", "r", encoding="utf-8") as f:
                packages = [
                    paragraph
                    for paragraph in deb822.Deb822.iter_paragraphs(f)
                    if paragraph.get("Status", "").startswith("install ok installed")
                ]
                packages.sort(key=lambda p: p.get("Package", ""))
                return InstalledPackages(packages)
        except (FileNotFoundError, PermissionError):
            return InstalledPackages([])

    def package_is_installed(self, package: str) -> bool:
        """Check if package is installed"""
        return self.collect_installed_packages().get_package(package) is not None

    def architecture_native(self) -> str:
        """Get the native architecture of the system"""
        with open("/var/lib/dpkg/arch-native") as f:
            return f.read().strip()

    def architectures_foreign(self) -> list[str]:
        """Get the foreign architectures of the system"""
        with open("/var/lib/dpkg/arch") as f:
            native = self.architecture_native()
            return list(filter(lambda x: x != native, f.read().split("\n")))

    def architectures(self) -> list[str]:
        """Get the native and foreign architectures of the system"""
        with open("/var/lib/dpkg/arch") as f:
            return list(filter(None, f.read().split("\n")))


@pytest.fixture
def dpkg(shell=None) -> Dpkg:
    return Dpkg(shell)
