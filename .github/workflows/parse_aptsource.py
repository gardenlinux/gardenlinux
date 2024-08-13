# SPDX-License-Identifier: MIT

# Based on code from glvd https://github.com/gardenlinux/glvd/blob/main/src/glvd/data/debsrc.py

from __future__ import annotations

import re
from typing import TextIO

class Debsrc():
    def __init__(self, deb_source, deb_version):
        self.deb_source = deb_source
        self.deb_version = deb_version

    deb_source: str
    deb_version: str

    def __repr__(self) -> str:
        return f"{self.deb_source} {self.deb_version}"


class DebsrcFile(dict[str, Debsrc]):
    __re = re.compile(r'''
        ^(?:
            Package:\s*(?P<source>[a-z0-9.-]+)
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

    def _read_source(self, source: str, version: str) -> None:
        self[source] = Debsrc(
            deb_source=source,
            deb_version=version,
        )

    def read(self, f: TextIO) -> None:
        current_source = current_version = None

        def finish():
            if current_source and current_version:
                self._read_source(current_source, current_version)

        for line in f.readlines():
            if match := self.__re.match(line):
                if i := match['source']:
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


if __name__ == '__main__':
    import sys

    d = DebsrcFile()
    with open(sys.argv[1]) as f:
        d.read(f)

    for entry in d.values():
        print(f'{entry!r}')
