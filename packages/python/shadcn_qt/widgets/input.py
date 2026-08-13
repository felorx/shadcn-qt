"""shadcn-style single-line input."""

from __future__ import annotations

from typing import Any, Optional

from shadcn_qt import _qt
from shadcn_qt.widgets._helpers import initialize_component, refresh_style
from shadcn_qt.widgets._style import install_shadow

_, _, QtWidgets = _qt.qt_modules()


class Input(QtWidgets.QLineEdit):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "input")
        self._invalid = False
        self.setFixedHeight(36)
        install_shadow(self, "xs")

    def is_invalid(self) -> bool:
        return self._invalid

    def set_invalid(self, invalid: bool) -> None:
        self._invalid = bool(invalid)
        refresh_style(self)

    isInvalid = is_invalid
    setInvalid = set_invalid
    invalid = _qt.qt_property(bool, fget=is_invalid, fset=set_invalid)


__all__ = ["Input"]
