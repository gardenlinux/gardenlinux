from typing import List

import boolean
import pytest

booleanAlgebra = boolean.BooleanAlgebra()


def setup_gardenlinux_features() -> set[str]:
    """
    Collects Garden Linux features and architecture information.
    """
    features = set[str]()
    with open("/etc/os-release") as os_release:
        for line in os_release:
            if line.startswith("GARDENLINUX_FEATURES="):
                _, value = line.split("=", 1)
                features = set(feature.strip() for feature in value.split(","))
    return features


features: set[str] = setup_gardenlinux_features()


def check_feature_condition(condition: str):
    """
    Evaluate if given feature condition is satisfied by the current set.
    Raises ValueError if the condition cannot be evaluated.
    """
    expr = booleanAlgebra.parse(condition)

    feature_symbols = {
        booleanAlgebra.Symbol(feature): booleanAlgebra.TRUE for feature in features
    }

    for symbol in expr.get_symbols():
        if symbol not in feature_symbols:
            feature_symbols[symbol] = booleanAlgebra.FALSE

    simplified = expr.subs(feature_symbols).simplify()

    try:
        return bool(simplified)
    except TypeError as e:
        unresolved = [str(sym) for sym in simplified.get_symbols()]
        raise ValueError(
            f"Cannot evaluate feature condition '{condition}'"
            f"Unresolved symbols after substitution: '{unresolved}'"
            f"Known features: {sorted(features)}"
        ) from e


def pytest_configure(config: pytest.Config):
    config.addinivalue_line(
        "markers",
        "feature(condition, reason=None): mark test to run only if feature set condition is met. Optionally provide a reason.",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    for item in items:
        for mark in item.iter_markers(name="feature"):
            condition = mark.args[0]
            reason = mark.kwargs.get("reason")
            skip_msg = f"excluded by feature condition: {condition}"
            if reason:
                skip_msg += f" (reason: {reason})"
            try:
                if not check_feature_condition(condition):
                    item.add_marker(pytest.mark.skip(reason=skip_msg))
            except ValueError as e:
                # Fail explicitly
                pytest.fail(f"Invalid feature condition in test '{item.name}': {e}")
