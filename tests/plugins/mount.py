import pytest


class Mount:
    def __init__(self, shell):
        self._shell = shell

    def __call__(self, shell, path):
        self._path = path

    def options(self):
        result = self._shell(
            f"findmnt -n -o 'OPTIONS' {self._path}", capture_output=True
        )
        return set(result.stdout.split(","))


@pytest.fixture
def mount(shell):
    return Mount(shell)
