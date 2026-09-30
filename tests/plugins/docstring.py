import inspect
from typing import List

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    for item in items:
        module = getattr(item, "module", None)
        func = getattr(item, "function", None)

        module_doc = inspect.getdoc(module) if module is not None else None
        func_doc = inspect.getdoc(func) if func is not None else None

        parts = [d for d in (module_doc, func_doc) if d]
        if parts:
            item.user_properties.append(("docstring", "\n\n".join(parts)))
