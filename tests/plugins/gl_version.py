"""
gl_version.py – pytest marker for version-aware cross-version testing.

Usage::

    @pytest.mark.gl_version(">1592.0.0", mode="skip")
    def test_new_behavior(client):
        ...

The ``<expr>`` argument is an operator (``>``, ``<``, or ``=``) followed
immediately by a SemVer version string.  The running Garden Linux version is
read from ``/etc/os-release`` via :func:`plugins.os_release.get_os_release`.

When the version constraint is **not** satisfied:

* ``mode="skip"``    – the test is not run.
* ``mode="warning"`` – the test runs; a failure is downgraded to a warning
  rather than a hard failure (default).
* ``mode="xfail"``   – the test runs; a failure is reported as an expected
  failure (xfail) rather than a hard failure.

When ``GARDENLINUX_VERSION`` is non-numeric (e.g. nightly/dev ``today``),
the constraint is treated as satisfied and a warning is emitted, so the
test always runs on such builds.
"""

import logging
import re
import warnings
from typing import List, Optional, Tuple

import pytest
from plugins.os_release import get_os_release

logger = logging.getLogger(__name__)

_VALID_OPERATORS = (">", "<", "=")
_EXPR_RE = re.compile(r"^([><]=?|=)(\d[\d.]*)$")

_VALID_MODES = ("skip", "warning", "xfail")
_DEFAULT_MODE = "warning"


# ---------------------------------------------------------------------------
# Expression parsing helpers
# ---------------------------------------------------------------------------


def _parse_expr(expr: str) -> Tuple[str, Tuple[int, ...]]:
    """Parse a constraint expression such as ``">1592.0.0"``.

    :returns: ``(operator, version_tuple)`` where ``operator`` is one of
        ``">"``, ``"<"``, ``"="``.
    :raises ValueError: on malformed expression or unsupported operator.
    """
    expr = expr.strip()
    m = _EXPR_RE.match(expr)
    if not m:
        raise ValueError(
            f"Invalid gl_version expression: {expr!r}. "
            f'Expected an operator (>, <, =) followed by a version, e.g. ">1592.0.0".'
        )
    op, version_str = m.group(1), m.group(2)
    if op not in _VALID_OPERATORS:
        raise ValueError(
            f"Unsupported operator {op!r} in gl_version expression {expr!r}. "
            f"Supported operators: {', '.join(_VALID_OPERATORS)}."
        )
    parts = version_str.split(".")
    try:
        if len(parts) == 2:
            version_tuple: Tuple[int, ...] = (int(parts[0]), int(parts[1]), 0)
        elif len(parts) == 3:
            version_tuple = (int(parts[0]), int(parts[1]), int(parts[2]))
        else:
            raise ValueError(
                f"Version {version_str!r} must have 2 or 3 numeric segments "
                f'(e.g. "1443.2" or "1592.0.0").'
            )
    except ValueError as exc:
        raise ValueError(
            f"Non-numeric version in gl_version expression {expr!r}: {exc}"
        ) from exc
    return op, version_tuple


def _evaluate_constraint(
    op: str,
    constraint_version: Tuple[int, ...],
    running_version: Tuple[int, ...],
) -> bool:
    """Return whether *running_version* satisfies *op constraint_version*."""
    if op == ">":
        return running_version > constraint_version
    if op == "<":
        return running_version < constraint_version
    if op == "=":
        return running_version == constraint_version
    raise AssertionError(f"Unhandled operator: {op!r}")  # pragma: no cover


def _check_constraint(expr: str) -> Optional[bool]:
    """Evaluate a constraint expression against the running Garden Linux version.

    :returns:
        ``True``  – constraint satisfied,
        ``False`` – constraint not satisfied,
        ``None``  – running version could not be determined (non-numeric).

    :raises ValueError: on malformed expression.
    """
    op, constraint_version = _parse_expr(expr)
    os_rel = get_os_release()
    running_tuple = os_rel.semver_tuple()
    logger.debug(f"GARDENLINUX_VERSION={os_rel.gardenlinux_version!r}")
    if running_tuple is None:
        return None  # non-numeric version
    return _evaluate_constraint(op, constraint_version, running_tuple)


def _add_error_marker(item: pytest.Item, message: str) -> None:
    """Mark *item* so it fails at run time with *message* as the failure reason.

    Using ``pytest.fail()`` directly in ``pytest_collection_modifyitems``
    causes an INTERNALERROR in pytest because the ``Failed`` exception is not
    caught there.  Instead we attach a hook that calls ``pytest.fail()``
    during the *setup* phase, which produces a proper ``ERROR`` result.
    """
    item._gl_version_error_message = message  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# pytest hooks
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        (
            "gl_version(expr, mode='warning'): run test only for matching Garden "
            "Linux versions; expr uses >, <, = against the version from "
            "/etc/os-release.  When the version does not match: "
            "skip = do not run; "
            "warning = run and downgrade a failure to a warning (default); "
            "xfail = run and mark a failure as xfail.  "
            "Non-numeric GARDENLINUX_VERSION (e.g. nightly 'today') is treated "
            "as satisfying any constraint; a warning is emitted."
        ),
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: List[pytest.Item]
) -> None:
    for item in items:
        marker = item.get_closest_marker("gl_version")
        if marker is None:
            continue

        if not marker.args:
            _add_error_marker(
                item,
                f"@pytest.mark.gl_version on '{item.name}' requires an expression "
                f'argument, e.g. @pytest.mark.gl_version(">1592.0.0").',
            )
            continue

        expr: str = marker.args[0]
        mode: str = marker.kwargs.get("mode", _DEFAULT_MODE)

        if mode not in _VALID_MODES:
            _add_error_marker(
                item,
                f"Invalid mode {mode!r} in @pytest.mark.gl_version on '{item.name}'. "
                f"Valid modes: {', '.join(_VALID_MODES)}.",
            )
            continue

        try:
            satisfied = _check_constraint(expr)
        except ValueError as exc:
            _add_error_marker(
                item,
                f"Invalid gl_version expression in test '{item.name}': {exc}",
            )
            continue

        if satisfied is None:
            # Non-numeric running version: treat as satisfied, emit a warning.
            os_rel = get_os_release()
            warnings.warn(
                f"gl_version constraint {expr!r} on '{item.name}' could not be "
                f"evaluated: GARDENLINUX_VERSION={os_rel.gardenlinux_version!r} is "
                f"non-numeric.  Treating the constraint as satisfied.",
                stacklevel=2,
            )
            # Test runs normally; nothing to add.
            continue

        if satisfied:
            # Constraint satisfied: test runs normally regardless of mode.
            continue

        # Constraint not satisfied — apply the requested mode.
        skip_reason = (
            f"gl_version constraint not satisfied: "
            f"{get_os_release().gardenlinux_version!r} "
            f"is not {expr!r}"
        )

        if mode == "skip":
            item.add_marker(pytest.mark.skip(reason=skip_reason))

        elif mode == "xfail":
            item.add_marker(
                pytest.mark.xfail(
                    reason=skip_reason,
                    strict=False,
                )
            )

        elif mode == "warning":
            # Store the reason on the item so the report hook can find it.
            item._gl_version_warning_reason = skip_reason  # type: ignore[attr-defined]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item: pytest.Item):
    """Fail tests that carry a gl_version error (invalid expression or mode).

    Calling ``pytest.fail()`` in ``pytest_collection_modifyitems`` causes an
    INTERNALERROR, so we defer the failure to the *setup* phase instead, which
    produces a proper ``ERROR`` outcome.
    """
    error_message = getattr(item, "_gl_version_error_message", None)
    yield
    if error_message is not None:
        pytest.fail(error_message)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    """Downgrade failures caused by unsatisfied gl_version(mode='warning') constraints.

    If a test has an unsatisfied ``gl_version`` constraint with
    ``mode='warning'`` and the call phase fails, the failure outcome is
    rewritten to ``"passed"`` and a pytest warning is emitted so the mismatch
    is visible without hard-failing the run.
    """
    outcome = yield
    report = outcome.get_result()

    if call.when != "call":
        return

    reason = getattr(item, "_gl_version_warning_reason", None)
    if reason is None:
        return

    if report.failed:
        # Downgrade hard failure to a warning.
        report.outcome = "passed"
        warnings.warn(
            f"gl_version(mode='warning'): test '{item.name}' failed but the "
            f"failure was downgraded to a warning because the version constraint "
            f"is not satisfied.  Reason: {reason}",
            stacklevel=2,
        )
