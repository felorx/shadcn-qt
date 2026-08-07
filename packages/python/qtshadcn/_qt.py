"""Detect and re-export Qt modules from a single installed binding (PySide6/PyQt6/PySide2/PyQt5)."""

from __future__ import annotations

import os
from typing import Any, Optional

_BINDING: Optional[str] = None
QtWidgets: Any = None
QtCore: Any = None
QtGui: Any = None

_VALID = frozenset({"PySide6", "PyQt6", "PySide2", "PyQt5"})


def _load(binding: str) -> None:
    global QtWidgets, QtCore, QtGui, _BINDING
    if binding == "PySide6":
        from PySide6 import QtCore as _QtCore  # type: ignore
        from PySide6 import QtGui as _QtGui  # type: ignore
        from PySide6 import QtWidgets as _QtWidgets  # type: ignore
    elif binding == "PyQt6":
        from PyQt6 import QtCore as _QtCore  # type: ignore
        from PyQt6 import QtGui as _QtGui  # type: ignore
        from PyQt6 import QtWidgets as _QtWidgets  # type: ignore
    elif binding == "PySide2":
        from PySide2 import QtCore as _QtCore  # type: ignore
        from PySide2 import QtGui as _QtGui  # type: ignore
        from PySide2 import QtWidgets as _QtWidgets  # type: ignore
    elif binding == "PyQt5":
        from PyQt5 import QtCore as _QtCore  # type: ignore
        from PyQt5 import QtGui as _QtGui  # type: ignore
        from PyQt5 import QtWidgets as _QtWidgets  # type: ignore
    else:
        raise ValueError(f"Unknown binding {binding}")
    QtCore, QtGui, QtWidgets, _BINDING = _QtCore, _QtGui, _QtWidgets, binding


def detect_binding(preferred: Optional[str] = None) -> str:
    """Load Qt modules. Respect QTSHADCN_QT_BINDING if set."""
    global _BINDING
    if _BINDING is not None:
        return _BINDING
    env = preferred or os.environ.get("QTSHADCN_QT_BINDING")
    order = ("PySide6", "PyQt6", "PySide2", "PyQt5")
    if env:
        if env not in _VALID:
            raise ValueError(
                f"QTSHADCN_QT_BINDING must be one of {sorted(_VALID)}, got {env!r}"
            )
        _load(env)
        return env
    last_err: Optional[BaseException] = None
    for name in order:
        try:
            _load(name)
            return name
        except Exception as e:  # noqa: BLE001
            last_err = e
            continue
    raise ImportError(
        "qtshadcn requires PySide6, PyQt6, PySide2, or PyQt5. "
        f"Last error: {last_err!r}"
    )


def app_exec(app: Any) -> None:
    """Qt6: app.exec(); Qt5 PyQt: app.exec_()."""
    exe = getattr(app, "exec", None)
    if callable(exe):
        exe()
        return
    exe_old = getattr(app, "exec_", None)
    if callable(exe_old):
        exe_old()
        return
    raise AttributeError("QApplication has neither exec nor exec_")
