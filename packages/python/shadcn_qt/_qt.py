"""Lazy, single-binding Qt compatibility helpers.

Importing :mod:`shadcn_qt` must not require Qt to be installed. Accessing one
of ``QtCore``, ``QtGui`` or ``QtWidgets`` loads the selected binding lazily.
"""

from __future__ import annotations

import importlib
import os
from typing import Any, Optional, Tuple

_BINDING: Optional[str] = None
_VALID = frozenset({"PySide6", "PyQt6", "PySide2", "PyQt5"})
_ORDER = ("PySide6", "PyQt6", "PySide2", "PyQt5")


def _load(binding: str) -> None:
    global _BINDING
    core = importlib.import_module(f"{binding}.QtCore")
    gui = importlib.import_module(f"{binding}.QtGui")
    widgets = importlib.import_module(f"{binding}.QtWidgets")
    globals()["QtCore"] = core
    globals()["QtGui"] = gui
    globals()["QtWidgets"] = widgets
    _BINDING = binding


def detect_binding(preferred: Optional[str] = None) -> str:
    """Load and return the active Qt binding.

    ``preferred`` and ``SHADCN_QT_BINDING`` are strict: a requested binding
    is never silently replaced by another one.
    """

    if _BINDING is not None:
        if preferred is not None and preferred != _BINDING:
            raise RuntimeError(
                f"Qt binding {_BINDING} is already loaded; cannot switch to {preferred}."
            )
        return _BINDING

    requested = preferred or os.environ.get("SHADCN_QT_BINDING")
    if requested:
        if requested not in _VALID:
            raise ValueError(
                f"SHADCN_QT_BINDING must be one of {sorted(_VALID)}, got {requested!r}"
            )
        try:
            _load(requested)
        except ImportError as exc:
            raise ImportError(
                f"shadcn-qt was configured to use {requested}, but it is not importable."
            ) from exc
        return requested

    errors = []
    for name in _ORDER:
        try:
            _load(name)
            return name
        except ImportError as exc:
            errors.append(f"{name}: {exc}")

    raise ImportError(
        "shadcn-qt requires one of PySide6, PyQt6, PySide2, or PyQt5. "
        "Install shadcn-qt with one binding extra, for example "
        "`pip install shadcn-qt[pyside6]`. Attempts: " + "; ".join(errors)
    )


def qt_modules() -> Tuple[Any, Any, Any]:
    """Return ``(QtCore, QtGui, QtWidgets)`` for the active binding."""

    detect_binding()
    return globals()["QtCore"], globals()["QtGui"], globals()["QtWidgets"]


def qt_property(*args: Any, **kwargs: Any) -> Any:
    """Cross-binding alias for ``Property`` / ``pyqtProperty``."""

    core, _, _ = qt_modules()
    factory = getattr(core, "Property", None) or getattr(core, "pyqtProperty")
    return factory(*args, **kwargs)


def qt_signal(*args: Any, **kwargs: Any) -> Any:
    """Cross-binding alias for ``Signal`` / ``pyqtSignal``."""

    core, _, _ = qt_modules()
    factory = getattr(core, "Signal", None) or getattr(core, "pyqtSignal")
    return factory(*args, **kwargs)


def import_qt_module(module: str) -> Any:
    """Import an optional module (for example ``QtUiTools``) from the binding."""

    binding = detect_binding()
    return importlib.import_module(f"{binding}.{module}")


def app_exec(app: Any) -> Any:
    """Run a QApplication on both Qt 5 and Qt 6."""

    execute = getattr(app, "exec", None) or getattr(app, "exec_", None)
    if not callable(execute):
        raise AttributeError("QApplication has neither exec nor exec_")
    return execute()


def __getattr__(name: str) -> Any:
    if name in {"QtCore", "QtGui", "QtWidgets"}:
        detect_binding()
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "QtCore",
    "QtGui",
    "QtWidgets",
    "app_exec",
    "detect_binding",
    "import_qt_module",
    "qt_modules",
    "qt_property",
    "qt_signal",
]
