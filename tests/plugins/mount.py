import pytest


class Mount:
    def __init__(self, shell):
        self._shell = shell
        self._options = set()

    def __call__(self, shell, path):
        self._path = path

    @property
    def options(self):
        if not self._options:
            result = self._shell(
                f"findmnt -n -o 'OPTIONS' {self._path}", capture_output=True
            )
            self._options = set(result.stdout.split(","))
        return self._options


@pytest.fixture
def mount(shell):
    return Mount(shell)
