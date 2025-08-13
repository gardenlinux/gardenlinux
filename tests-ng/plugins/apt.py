import pytest
from .shell import ShellRunner

class Apt:
    def __init__(self, shell: ShellRunner):
        self._shell = shell

    def list_repos(self) -> list[str]:
        """
        Lists the configured APT repositories by parsing the output of 'apt-cache policy'.
        Returns a list of repository URLs.
        """
        result = self._shell('apt-cache policy', capture_output=True, ignore_exit_code=True)
        repos = set()
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if 'https' in line:
                    repos.add(line.split()[1])
        return list(repos)
