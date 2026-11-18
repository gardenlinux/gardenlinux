"""Unit tests for the @pytest.mark.gl_version marker (plugins.gl_version)."""

import warnings
from unittest.mock import MagicMock, patch

import pytest
from plugins.gl_version import (
    _check_constraint,
    _parse_expr,
    pytest_collection_modifyitems,
)
from plugins.os_release import OsRelease

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _patch_os_release(version):
    """Patch get_os_release() in gl_version to return a fixed version string."""
    return patch(
        "plugins.gl_version.get_os_release",
        return_value=OsRelease(gardenlinux_version=version),
    )


class _FakeMarker:
    """Minimal stand-in for a pytest Mark as seen by gl_version hooks."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class _FakeItem:
    """Minimal stand-in for a pytest.Item sufficient to test pytest_collection_modifyitems.

    NOTE: pytest_collection_modifyitems does not use the `config` argument.
    A MagicMock() is passed to satisfy pyright's type check.
    """

    def __init__(self, expr, mode=None, name="test_fake"):
        kwargs = {} if mode is None else {"mode": mode}
        self._marker = (
            _FakeMarker(expr, **kwargs) if expr is not None else _FakeMarker()
        )
        self.name = name
        self.added_markers = []

    def get_closest_marker(self, name):
        return self._marker if name == "gl_version" else None

    def add_marker(self, marker):
        self.added_markers.append(marker)


def _run_hook(item, version="1592.0.0"):
    """Run pytest_collection_modifyitems on a single fake item with a patched version."""
    with _patch_os_release(version):
        pytest_collection_modifyitems(config=MagicMock(), items=[item])


# ---------------------------------------------------------------------------
# _parse_expr unit tests
# ---------------------------------------------------------------------------


def test_parse_expr_greater_than():
    op, ver = _parse_expr(">1592.0.0")
    assert op == ">"
    assert ver == (1592, 0, 0)


def test_parse_expr_less_than():
    op, ver = _parse_expr("<2150.0.0")
    assert op == "<"
    assert ver == (2150, 0, 0)


def test_parse_expr_equal():
    op, ver = _parse_expr("=1443.0.0")
    assert op == "="
    assert ver == (1443, 0, 0)


def test_parse_expr_two_segment_version():
    op, ver = _parse_expr(">1443.2")
    assert op == ">"
    assert ver == (1443, 2, 0)


def test_parse_expr_strips_whitespace():
    op, ver = _parse_expr("  >1592.0.0  ")
    assert op == ">"
    assert ver == (1592, 0, 0)


def test_parse_expr_invalid_no_operator():
    with pytest.raises(ValueError, match="Invalid gl_version expression"):
        _parse_expr("1592.0.0")


@pytest.mark.parametrize("expr", [">=1592.0.0", "<=1592.0.0"])
def test_parse_expr_invalid_unsupported_operator(expr):
    with pytest.raises(ValueError):
        _parse_expr(expr)


def test_parse_expr_non_numeric_version():
    with pytest.raises(ValueError):
        _parse_expr(">today")


def test_parse_expr_single_segment_version_rejected():
    with pytest.raises(ValueError, match="2 or 3 numeric segments"):
        _parse_expr(">2016")


# ---------------------------------------------------------------------------
# _check_constraint unit tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expr,running,expected",
    [
        # Greater-than
        (">1592.0.0", "2150.0.0", True),
        (">1592.0.0", "1592.0.0", False),
        (">1592.0.0", "1443.0.0", False),
        # Less-than
        ("<1592.0.0", "1443.0.0", True),
        ("<1592.0.0", "1592.0.0", False),
        ("<1592.0.0", "2150.0.0", False),
        # Equal
        ("=1592.0.0", "1592.0.0", True),
        ("=1592.0.0", "1443.0.0", False),
        ("=1592.0.0", "2150.0.0", False),
        # Legacy 2-segment and cross-boundary
        (">1443.0", "1443.2", True),
        ("<2017.0.0", "2016.0", True),
        (">2016.0", "2017.0.0", True),
        ("=2016.0", "2016.0", True),
        ("=2016.0", "2016.0.0", True),
        (">2016.0", "2016.0", False),
    ],
)
def test_check_constraint_operators(expr, running, expected):
    with _patch_os_release(running):
        result = _check_constraint(expr)
    assert result is expected


def test_check_constraint_non_numeric_running_version_returns_none():
    with _patch_os_release("today"):
        result = _check_constraint(">1592.0.0")
    assert result is None


# ---------------------------------------------------------------------------
# Mode-selection tests via pytest_collection_modifyitems + FakeItem
# ---------------------------------------------------------------------------


def test_mode_skip_unsatisfied_adds_skip_marker():
    """Unsatisfied constraint with mode=skip → skip marker added."""
    item = _FakeItem(">1592.0.0", mode="skip")
    _run_hook(item, version="1443.0.0")
    assert len(item.added_markers) == 1
    assert item.added_markers[0].name == "skip"


def test_mode_skip_satisfied_no_marker():
    """Satisfied constraint with mode=skip → nothing added."""
    item = _FakeItem(">1592.0.0", mode="skip")
    _run_hook(item, version="2150.0.0")
    assert item.added_markers == []
    assert not hasattr(item, "_gl_version_warning_reason")
    assert not hasattr(item, "_gl_version_error_message")


def test_mode_xfail_unsatisfied_adds_xfail_marker():
    """Unsatisfied constraint with mode=xfail → xfail marker added."""
    item = _FakeItem(">1592.0.0", mode="xfail")
    _run_hook(item, version="1443.0.0")
    assert len(item.added_markers) == 1
    assert item.added_markers[0].name == "xfail"


def test_mode_warning_unsatisfied_sets_warning_reason():
    """Unsatisfied constraint with mode=warning → warning reason set, no skip/xfail marker."""
    item = _FakeItem(">1592.0.0", mode="warning")
    _run_hook(item, version="1443.0.0")
    assert item.added_markers == []
    assert getattr(item, "_gl_version_warning_reason", None) is not None


def test_mode_default_is_warning():
    """Default mode (no mode kwarg) behaves like mode=warning."""
    item = _FakeItem(">1592.0.0")  # no mode
    _run_hook(item, version="1443.0.0")
    assert item.added_markers == []
    assert getattr(item, "_gl_version_warning_reason", None) is not None


def test_invalid_expression_sets_error_message():
    """Invalid expression (>=) → error message set on item."""
    item = _FakeItem(">=1592.0.0")
    _run_hook(item, version="1592.0.0")
    assert getattr(item, "_gl_version_error_message", None) is not None
    assert item.added_markers == []


def test_invalid_mode_sets_error_message():
    """Unknown mode → error message set on item."""
    item = _FakeItem(">1592.0.0", mode="unknown")
    _run_hook(item, version="1592.0.0")
    assert getattr(item, "_gl_version_error_message", None) is not None
    assert item.added_markers == []


def test_non_numeric_running_version_treats_constraint_as_satisfied():
    """Non-numeric GARDENLINUX_VERSION (e.g. 'today') → constraint satisfied, mode=skip does not skip."""
    item = _FakeItem(">1592.0.0", mode="skip")
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        _run_hook(item, version="today")
    assert item.added_markers == []
    assert not hasattr(item, "_gl_version_warning_reason")
