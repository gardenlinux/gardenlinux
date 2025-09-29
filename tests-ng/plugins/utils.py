from pathlib import Path
from typing import Dict, List, Optional

import pytest

# Various utility functions to make tests more readable
# This should not contain test-assertions, but only abstract details that make tests harder to read


def equals_ignore_case(a: str, b: str) -> bool:
    return a.casefold() == b.casefold()


def get_normalized_sets(*sets: set) -> tuple[set, ...]:
    normalized_sets = tuple({str(v).casefold() for v in s} for s in sets)
    return normalized_sets


def is_set(obj) -> bool:
    return isinstance(obj, set)


def parse_etc_file(
    path: Path, field_names: List[str], min_fields: Optional[int] = None
) -> List[Dict[str, str | List[str]]]:
    """
    Generic parser for /etc/* files into structured dictionaries.

    Example:
        /etc/passwd line:
            root:x:0:0:root:/root:/bin/bash

        field_names = ["user", "passwd", "uid", "gid"]
        ->
        {
            "user": "root",
            "passwd": "x",
            "uid": "0",
            "gid": "0",
            "rest": ["root", "/root", "/bin/bash"]
        }

    :param path: Path to the file (e.g. /etc/passwd, /etc/shadow).
    :param field_names: Names for the desired relevant fields.
    :param min_fields: Minimum required number of colon-separated fields per line.
                       Defaults to len(field_names).
    :return: List of dicts with the given field_names plus "rest" for extra fields.
    :raises FileNotFoundError: if the file does not exist
    :raises PermissionError: if the file cannot be read
    :raises ValueError: if a line is malformed
    """
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        raise FileNotFoundError(f"Required file not found: {path}")
    except PermissionError:
        raise PermissionError(f"Permission denied while attempting to read '{path}'")

    if min_fields is None:
        min_fields = len(field_names)

    entries: List[Dict[str, str | List[str]]] = []
    for line in content.splitlines():
        if not line.strip() or line.startswith("#"):
            continue  # Skip comments and empty lines

        fields = line.split(":")
        if len(fields) < min_fields:
            raise ValueError(f"Malformed line in {path}: {line!r}")

        entry: Dict[str, str | List[str]] = {}
        # Assign the first N fields to the provided field_names
        for i, name in enumerate(field_names):
            if i < len(fields):
                entry[name] = fields[i]

        # Store any remaining fields in a list
        entry["rest"] = fields[len(field_names) :]
        entries.append(entry)

    return entries
