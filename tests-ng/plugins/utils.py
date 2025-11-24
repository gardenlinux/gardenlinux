from typing import List, TypeVar

# Various utility functions to make tests more readable
# This should not contain test-assertions, but only abstract details that make tests harder to read


def equals_ignore_case(a: str, b: str) -> bool:
    return a.casefold() == b.casefold()


def get_normalized_sets(*sets: set) -> tuple[set, ...]:
    normalized_sets = tuple({str(v).casefold() for v in s} for s in sets)
    return normalized_sets


def is_set(obj) -> bool:
    return isinstance(obj, set)


T = TypeVar("T")


def check_for_duplicates(entries: List[T]) -> List[T]:
    """
    checks for duplicates, to change equality comparision, add a compare field to the dataclass.
    """
    duplicates = list[T]()
    visited_entries = list[T]()
    for entry in entries:
        if entry in visited_entries:
            duplicates.append(entry)
        else:
            visited_entries.append(entry)

    return duplicates
