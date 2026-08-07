"""shadcn-style Card container (QFrame)."""

from __future__ import annotations

from typing import Optional

from qtshadcn._qt import QtWidgets, detect_binding

detect_binding()


class Card(QtWidgets.QFrame):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("qtshadcn-card")
        F = QtWidgets.QFrame
        shape = getattr(F, "StyledPanel", None)
        if shape is None:
            shape = F.Shape.StyledPanel
        shadow = getattr(F, "Plain", None)
        if shadow is None:
            shadow = F.Shadow.Plain
        self.setFrameShape(shape)
        self.setFrameShadow(shadow)
