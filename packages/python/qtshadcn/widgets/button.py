"""shadcn-style Button with Qt Designer-editable properties."""

from __future__ import annotations

from typing import Any, Literal, Optional, Union

from qtshadcn import _qt
from qtshadcn.widgets._helpers import initialize_component, set_choice_property

ButtonVariant = Literal[
    "default", "destructive", "outline", "secondary", "ghost", "link"
]
ButtonSize = Literal["default", "sm", "lg", "icon"]

_, _, QtWidgets = _qt.qt_modules()


class Button(QtWidgets.QPushButton):
    """QPushButton with shadcn variants and sizes.

    ``Button(parent)`` is supported for generated ``.ui`` code, while
    ``Button("Save", parent, variant="outline")`` remains convenient by hand.
    """

    VARIANTS = ("default", "destructive", "outline", "secondary", "ghost", "link")
    SIZES = ("default", "sm", "lg", "icon")

    def __init__(
        self,
        text: Union[str, Any] = "",
        parent: Optional[Any] = None,
        *,
        variant: ButtonVariant = "default",
        size: ButtonSize = "default",
    ) -> None:
        if isinstance(text, QtWidgets.QWidget) and parent is None:
            parent, text = text, ""
        super().__init__(str(text), parent)
        initialize_component(self, "button")
        self._variant = "default"
        self._shadcn_size = "default"
        self.set_variant(variant)
        self.set_shadcn_size(size)

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, variant: str) -> None:
        set_choice_property(self, "_variant", "variant", variant, self.VARIANTS)
        self.setProperty("qtshadcn_variant", variant)  # 0.1 compatibility

    getVariant = get_variant
    setVariant = set_variant
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)

    def get_shadcn_size(self) -> str:
        return self._shadcn_size

    def set_shadcn_size(self, size: str) -> None:
        set_choice_property(self, "_shadcn_size", "shadcnSize", size, self.SIZES)
        self.setProperty("qtshadcn_size", size)  # 0.1 compatibility

    getShadcnSize = get_shadcn_size
    setShadcnSize = set_shadcn_size
    shadcnSize = _qt.qt_property(str, fget=get_shadcn_size, fset=set_shadcn_size)


__all__ = ["Button", "ButtonSize", "ButtonVariant"]
