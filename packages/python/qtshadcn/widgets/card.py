"""shadcn-style Card container."""

from __future__ import annotations

from typing import Any, Optional

from qtshadcn import _qt
from qtshadcn.widgets._helpers import initialize_component, refresh_style

_, _, QtWidgets = _qt.qt_modules()


class Card(QtWidgets.QFrame):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "card")
        frame = QtWidgets.QFrame
        shape = getattr(frame, "StyledPanel", None)
        shadow = getattr(frame, "Plain", None)
        if shape is None:
            shape = frame.Shape.StyledPanel
        if shadow is None:
            shadow = frame.Shadow.Plain
        self.setFrameShape(shape)
        self.setFrameShadow(shadow)
        self._elevated = False

    def is_elevated(self) -> bool:
        return self._elevated

    def set_elevated(self, elevated: bool) -> None:
        self._elevated = bool(elevated)
        refresh_style(self)

    isElevated = is_elevated
    setElevated = set_elevated
    elevated = _qt.qt_property(bool, fget=is_elevated, fset=set_elevated)


__all__ = ["Card"]
