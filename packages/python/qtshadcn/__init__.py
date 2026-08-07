"""qtshadcn — shadcn-aligned Qt widgets and themes for PySide / PyQt."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from qtshadcn.theme import apply_palette_from_tokens, apply_theme
from qtshadcn._qt import app_exec, detect_binding

__all__ = [
    "Button",
    "Card",
    "Input",
    "apply_theme",
    "apply_palette_from_tokens",
    "app_exec",
    "detect_binding",
]


def __getattr__(name: str) -> Any:
    if name == "Button":
        from qtshadcn.widgets.button import Button

        return Button
    if name == "Card":
        from qtshadcn.widgets.card import Card

        return Card
    if name == "Input":
        from qtshadcn.widgets.input import Input

        return Input
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if TYPE_CHECKING:
    from qtshadcn.widgets.button import Button as Button
    from qtshadcn.widgets.card import Card as Card
    from qtshadcn.widgets.input import Input as Input
