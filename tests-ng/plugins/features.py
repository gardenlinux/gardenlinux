import boolean
import pytest

booleanAlgebra = boolean.BooleanAlgebra()

with open("/etc/os-release") as os_release:
	for line in os_release:
		(key, value) = line.split("=", 1)
		if key == "GARDENLINUX_FEATURES":
			features = set([ feature.strip() for feature in value.split(",") ])

def check_feature_condition(condition):
	feature_symbols = { booleanAlgebra.Symbol(feature): booleanAlgebra.TRUE for feature in features }
	expr = booleanAlgebra.parse(condition)
	for symbol in expr.get_symbols():
		if symbol not in feature_symbols:
			feature_symbols[symbol] = booleanAlgebra.FALSE
	return bool(expr.subs(feature_symbols).simplify())

def pytest_configure(config):
	config.addinivalue_line("markers", "feature(condition): mark test to run only if feature set condition is met")

def pytest_collection_modifyitems(config, items):
	for item in items:
		for mark in item.iter_markers(name="feature"):
			condition = mark.args[0]
			if not check_feature_condition(condition):
				item.add_marker(pytest.mark.skip(reason=f"excluded by feature condition: {condition}"))
