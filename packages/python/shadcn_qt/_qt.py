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


def _enum_value(namespace: Any, name: str, group: str) -> Any:
    value = getattr(namespace, name, None)
    if value is not None:
        return value
    return getattr(getattr(namespace, group), name)


def _configure_high_dpi_defaults(core: Any, gui: Any) -> bool:
    """Apply the process-wide DPI contract before QApplication exists."""

    if core.QCoreApplication.instance() is not None:
        return False

    qt_major = int(str(core.qVersion()).split(".", 1)[0])
    if qt_major < 6:
        for attribute_name in (
            "AA_EnableHighDpiScaling",
            "AA_UseHighDpiPixmaps",
        ):
            attribute = _enum_value(
                core.Qt,
                attribute_name,
                "ApplicationAttribute",
            )
            core.QCoreApplication.setAttribute(attribute, True)

    pass_through = _enum_value(
        core.Qt,
        "PassThrough",
        "HighDpiScaleFactorRoundingPolicy",
    )
    gui.QGuiApplication.setHighDpiScaleFactorRoundingPolicy(pass_through)
    return True


def _load(binding: str) -> None:
    global _BINDING
    core = importlib.import_module(f"{binding}.QtCore")
    gui = importlib.import_module(f"{binding}.QtGui")
    widgets = importlib.import_module(f"{binding}.QtWidgets")
    _configure_high_dpi_defaults(core, gui)
    globals()["QtCore"] = core
    globals()["QtGui"] = gui
    globals()["QtWidgets"] = widgets
    _BINDING = binding


def _canonical_binding(name: str) -> str:
    """Return the documented spelling of ``name``, ignoring case and padding."""

    candidate_name = name.strip().casefold()
    for candidate in _ORDER:
        if candidate.casefold() == candidate_name:
            return candidate
    return name


def detect_binding(preferred: Optional[str] = None) -> str:
    """Load and return the active Qt binding.

    ``preferred`` and ``SHADCN_QT_BINDING`` are strict: a requested binding
    is never silently replaced by another one. The spelling is matched
    case-insensitively, so ``pyqt6`` selects ``PyQt6``.
    """

    if _BINDING is not None:
        if preferred is not None and _canonical_binding(preferred) != _BINDING:
            raise RuntimeError(
                f"Qt binding {_BINDING} is already loaded; cannot switch to {preferred}."
            )
        return _BINDING

    requested_name = preferred or os.environ.get("SHADCN_QT_BINDING")
    if requested_name:
        requested = _canonical_binding(requested_name)
        if requested not in _VALID:
            raise ValueError(
                f"SHADCN_QT_BINDING must be one of {sorted(_VALID)}, "
                f"got {requested_name!r}"
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


def configure_high_dpi() -> None:
    """Configure precise high-DPI scaling before creating QApplication.

    The selected Qt binding is loaded lazily, Qt 5 high-DPI support is enabled,
    and fractional operating-system scale factors such as Windows 150% remain
    fractional instead of being rounded to 200%.
    """

    detect_binding()
    core = globals()["QtCore"]
    gui = globals()["QtGui"]
    if core.QCoreApplication.instance() is not None:
        raise RuntimeError(
            "configure_high_dpi() must be called before creating QApplication"
        )
    _configure_high_dpi_defaults(core, gui)


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
    "configure_high_dpi",
    "detect_binding",
    "import_qt_module",
    "qt_modules",
    "qt_property",
    "qt_signal",
]
