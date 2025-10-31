import json
from dataclasses import dataclass

import pytest
from plugins.shell import ShellRunner


@dataclass
class Chain:
    family: str
    table: str
    name: str
    handle: int
    type: str
    hook: str
    prio: int
    policy: str


@dataclass
class TableInterFilter:
    chains: list[Chain]


class Nft:
    def __init__(self, shell: ShellRunner):
        self._shell = shell

    def list_table_inet_filter(self) -> list[Chain]:
        result = self._shell(
            cmd="nft -j list table inet filter",
            capture_output=True,
            ignore_exit_code=True,
        )
        if result.returncode != 0:
            raise ValueError(f"nft list table inet filter failed: {result.stderr}")

        output_json = json.loads(result.stdout)
        return [
            Chain(**obj["chain"]) for obj in output_json["nftables"] if obj.get("chain")
        ]


@pytest.fixture
def nft(shell: ShellRunner):
    return Nft(shell)
