import pytest

from .shell import ShellRunner


class Dpkg:
    def __init__(self, shell: ShellRunner):
        self._shell = shell

    def package_is_installed(self, package: str) -> bool:
        arches = self.own_and_foreign_architectures()
        is_installed = True
        for arch in arches:
            result = self._shell(
                f"dpkg --status {package}:{arch}",
                capture_output=True,
                ignore_exit_code=True,
            )
            is_installed = is_installed and result.returncode == 0
        return is_installed

    def architecture(self) -> str:
        result = self._shell(
            "dpkg --print-architecture", capture_output=True, ignore_exit_code=True
        )
        return result.stdout.strip()

    def foreign_architectures(self) -> list[str]:
        result = self._shell(
            "dpkg --print-foreign-architectures",
            capture_output=True,
            ignore_exit_code=True,
        )
        return list(filter(None, result.stdout.split("\n")))

    def own_and_foreign_architectures(self) -> list[str]:
        architectures = self.foreign_architectures()
        architectures.append(self.architecture())
        return architectures


@pytest.fixture
def dpkg(shell: ShellRunner) -> Dpkg:
    return Dpkg(shell)
