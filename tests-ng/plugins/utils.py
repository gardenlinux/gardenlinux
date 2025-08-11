import pytest

# Various utility functions to make tests more readable
# This should not contain test-assertions, but only abstract details that make tests harder to read

def equals_ignore_case(a: str, b: str) -> str:
    return a.casefold() == b.casefold()


def get_normalized_sets(
    actual_value: set,
    expected_value: set,
) -> tuple[set, set]:
    actual_set = {str(v).casefold() for v in actual_value}
    expected_set = {str(v).casefold() for v in expected_value}
    return actual_set, expected_set


def is_set(obj) -> bool:
    return isinstance(obj, set)
