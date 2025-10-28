import os
import re
import string
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pytest


def parse_etc_file(
    path: Path,
    *,
    field_names: Optional[Iterable[str]] = None,
    min_fields: int = 1,
    sep: str = ":",
    skip_comments: bool = True,
    strip_whitespace: bool = True,
) -> List[Dict[str, str | List[str]]]:
    """
    Generic parser for /etc/* style files (passwd, shadow, group, etc.).
    - path: Path to the file (e.g., Path('/etc/passwd'))
    - field_names: optional iterable of names to assign to fields.
        * If provided and fewer than the number of fields on a line,
          all remaining fields are collected into the **last** name as a list.
        * If more names than fields exist on a line, the missing ones are set to ''.
    - min_fields: assert each non-empty, non-comment line has at least this many fields.
    - sep: field separator (default ':').
    Returns: list of dicts; values are str, except the last named field may be List[str]
             when there are extra trailing fields.
    """
    assert path.is_file(), f"File not found: {path}"
    text = path.read_text(encoding="utf-8", errors="ignore")

    names: List[str] = list(field_names) if field_names else []
    out: List[Dict[str, str | List[str]]] = []

    for raw in text.splitlines():
        line = raw.strip() if strip_whitespace else raw
        if not line:
            continue
        if skip_comments and line.startswith("#"):
            continue

        parts = line.split(sep)
        assert len(parts) >= min_fields, (
            f"Malformed line in {path}: expected >= {min_fields} fields, got {len(parts)}\n"
            f"Line: {raw!r}"
        )

        if not names:
            entry = {f"f{i}": v for i, v in enumerate(parts)}
            out.append(entry)
            continue

        if len(names) == 1:
            out.append({names[0]: parts})
            continue

        head_names = names[:-1]
        tail_name = names[-1]

        entry: Dict[str, str | List[str]] = {}
        for i, n in enumerate(head_names):
            entry[n] = parts[i] if i < len(parts) else ""

        rest = parts[len(head_names) :]
        if len(rest) <= 1:
            entry[tail_name] = rest[0] if rest else ""
        else:
            entry[tail_name] = rest

        out.append(entry)

    return out


def equals_ignore_case(a: str, b: str) -> bool:
    """Return True if both strings are equal ignoring case, else False."""
    return a.lower() == b.lower()

def get_normalized_sets(*iterables: Iterable) -> tuple[set[str], ...]:
    """
    Accepts ANY number of iterables and returns a tuple of normalized sets.
    Example:
        get_normalized_sets(['SSH'], ['ssh ', ' sSh'])
        -> ({'ssh'}, {'ssh'})
    """
    return tuple({str(x).strip().lower() for x in iterable} for iterable in iterables)


def is_set(value) -> bool:
    """Return True if the given value is a Python set."""
    return isinstance(value, set)
