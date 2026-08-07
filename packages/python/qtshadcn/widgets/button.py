"""shadcn-style Button (QPushButton + variants)."""

from __future__ import annotations

from typing import Literal, Optional

from qtshadcn._qt import QtWidgets, detect_binding

ButtonVariant = Literal["default", "destructive", "outline", "secondary", "ghost", "link"]
ButtonSize = Literal["default", "sm", "lg", "icon"]

detect_binding()


class Button(QtWidgets.QPushButton):
    """QPushButton with ``objectName`` and dynamic properties for generated QSS."""

    def __init__(
        self,
        text: str = "",
        parent: Optional[QtWidgets.QWidget] = None,
        *,
        variant: ButtonVariant = "default",
        size: ButtonSize = "default",
    ) -> None:
        super().__init__(text, parent)
        self.setObjectName("qtshadcn-button")
        self._variant = variant
        self._size = size
        self.setProperty("qtshadcn_variant", variant)
        self.setProperty("qtshadcn_size", size)
        self._refresh_style()

    def set_variant(self, variant: ButtonVariant) -> None:
        self._variant = variant
        self.setProperty("qtshadcn_variant", variant)
        self._refresh_style()

    def set_shadcn_size(self, size: ButtonSize) -> None:
        self._size = size
        self.setProperty("qtshadcn_size", size)
        self._refresh_style()

    def _refresh_style(self) -> None:
        style = self.style()
        if style is not None:
            style.unpolish(self)
            style.polish(self)
