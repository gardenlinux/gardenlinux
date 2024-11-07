# SPDX-License-Identifier: MIT

# Based on code from glvd https://github.com/gardenlinux/glvd/blob/99fccc41df13fc898ffc240cd41d8bc0eb5b3991/src/glvd/data/debsrc.py

# Parse Apt Package Index files, both of binary and of name packages

from __future__ import annotations

import re
from typing import TextIO

class DebianPackage():
    def __init__(self, name, version):
        self.name = name
        self.version = version

    name: str
    version: str

    def __repr__(self) -> str:
        return f"{self.name} {self.version}"


class DebianPackageIndexFile(dict[str, DebianPackage]):
    __re = re.compile(r'''
        ^(?:
            Package:\s*(?P<name>[a-z0-9.-]+)
            |
            Version:\s*(?P<version>[A-Za-z0-9.+~:-]+)
            |
            Extra-Source-Only:\s*(?P<eso>yes)
            |
            (?P<eoe>)
            |
            # All other fields
            [A-Za-z0-9-]+:.*
            |
            # Continuation field
            \s+.*
        )$
    ''', re.VERBOSE)

    def _read_source(self, name: str, version: str) -> None:
        self[name] = DebianPackage(
            name=name,
            version=version,
        )

    def read(self, f: TextIO) -> None:
        current_source = current_version = None

        def finish():
            if current_source and current_version:
                self._read_source(current_source, current_version)

        for line in f.readlines():
            if match := self.__re.match(line):
                if i := match['name']:
                    current_source = i
                elif i := match['version']:
                    current_version = i
                elif match['eso']:
                    current_source = current_version = None
                elif match['eoe'] is not None:
                    finish()
                    current_source = current_version = None
            else:
                raise RuntimeError(f'Unable to read line: {line}')

        finish()


def main(filename):
    with open(filename) as f:
        print(read_file(f))

def read_file(file):
    result = ''
    d = DebianPackageIndexFile()
    d.read(file)

    for entry in d.values():
        result += f'{entry!r}\n'
    return result

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    main(filename)

def test_parse_binary():
    with open('Test-Case-Binary-Packages.txt') as f:
        actual = read_file(f)
        assert len(actual.splitlines()) == 6


def test_parse_source():
    with open('Test-Case-Source-Packages.txt') as f:
        actual = read_file(f)
        assert len(actual.splitlines()) == 2
