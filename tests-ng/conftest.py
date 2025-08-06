import os
import pytest

plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
pytest_plugins = [
    f"plugins.{f[:-3]}"
    for f in os.listdir(plugin_dir)
    if f.endswith(".py") and not f.startswith("_")
]
