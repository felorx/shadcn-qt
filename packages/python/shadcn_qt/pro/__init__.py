"""Compatibility bridge for the separately distributed shadcn-qt Pro package.

The public Core wheel never contains Pro implementation code.  Customers with a
Pro entitlement install the private ``shadcn-qt-pro`` distribution, whose import
package is ``shadcn_qt_pro``.  This module only forwards its public API so older
``shadcn_qt.pro`` imports keep working without creating a split package across
two distributions.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

try:
    _pro = import_module("shadcn_qt_pro")
except ModuleNotFoundError as exc:
    if exc.name != "shadcn_qt_pro":
        raise
    raise ImportError(
        "shadcn_qt.pro requires the private shadcn-qt-pro distribution and a "
        "separate Pro entitlement; the public shadcn-qt Core package does not "
        "include Pro implementation code."
    ) from None

__all__ = list(getattr(_pro, "__all__", ()))


def __getattr__(name: str) -> Any:
    return getattr(_pro, name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_pro)))


for _name in __all__:
    globals()[_name] = getattr(_pro, _name)
