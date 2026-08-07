"""shadcn-style Input (QLineEdit)."""

from __future__ import annotations

from typing import Optional

from qtshadcn._qt import QtWidgets, detect_binding

detect_binding()


class Input(QtWidgets.QLineEdit):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("qtshadcn-input")
