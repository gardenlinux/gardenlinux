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
