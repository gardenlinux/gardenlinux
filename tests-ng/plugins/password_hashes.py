from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pytest

SUPPORTED_HASH_ALGORITHMS = ["yescrypt", "sha512"]


@dataclass
class PamEntry:
    type_: str
    control: str
    module: str
    options: List[str]

    @property
    def hash_algo(self) -> Optional[str]:
        """Return the hash algorithm specified in the options, if any."""
        for arg in self.args:
            if arg in SUPPORTED_HASH_ALGORITHMS:
                return arg
        return None


class PamConfig:
    def __init__(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"PAM config file at '{path}' not found!")
        self.path = path
        self.lines = [
            line.rstrip()
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
        ]
        self.entries: List[PamEntry] = self._parse_entries()

    def _parse_entries(self) -> List[PamEntry]:
        entries = []
        for line in self.lines:
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            # Split into tokens: tpye, control, module, args
            tokens = stripped.split()
            if len(tokens) < 3:
                continue  # skip malformed line
            type_, control, module, *args = tokens
            entries.append(PamEntry(type_, control, module, args))
        return entries

    def find_entries(
        self,
        type_: Optional[str] = None,
        module_contains: Optional[str] = None,
        arg_contains: Optional[List[str]] = None,
    ) -> List[PamEntry]:
        results = self.entries
        if type_:
            results = [e for e in results if e.type_.lower() == type_.lower()]
        if module_contains:
            results = [e for e in results if module_contains in e.module]
        if arg_contains:
            results = [
                e for e in results if all(token in e.args for token in arg_contains)
            ]
        return results


@pytest.fixture
def pam_config():
    """
    Return a PamConfig object for /etc/pam.d/common-password.
    """
    path = Path("/etc/pam.d/common-password")
    return PamConfig(path)
