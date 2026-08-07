"""qtshadcn — shadcn-aligned Qt widgets and customizable themes."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from qtshadcn._qt import app_exec, detect_binding
from qtshadcn.designer.loader import load_ui
from qtshadcn.theme import (
    Theme,
    ThemeConfig,
    ThemeMode,
    apply_palette_from_tokens,
    apply_theme,
    available_themes,
    configure,
    create_theme,
    current_theme,
    load_theme,
    register_theme,
    theme_stylesheet,
)

_WIDGET_NAMES = frozenset(
    {
        "Alert",
        "Badge",
        "Button",
        "Card",
        "Checkbox",
        "Input",
        "Label",
        "Progress",
        "RadioButton",
        "Select",
        "Separator",
        "Slider",
        "Switch",
        "Tabs",
        "TextArea",
    }
)

__all__ = sorted(_WIDGET_NAMES) + [
    "Theme",
    "ThemeConfig",
    "ThemeMode",
    "apply_palette_from_tokens",
    "apply_theme",
    "app_exec",
    "available_themes",
    "configure",
    "create_theme",
    "current_theme",
    "detect_binding",
    "load_theme",
    "load_ui",
    "register_theme",
    "theme_stylesheet",
]


def __getattr__(name: str) -> Any:
    if name in _WIDGET_NAMES:
        from qtshadcn import widgets

        return getattr(widgets, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if TYPE_CHECKING:
    from qtshadcn.widgets import (
        Alert as Alert,
        Badge as Badge,
        Button as Button,
        Card as Card,
        Checkbox as Checkbox,
        Input as Input,
        Label as Label,
        Progress as Progress,
        RadioButton as RadioButton,
        Select as Select,
        Separator as Separator,
        Slider as Slider,
        Switch as Switch,
        Tabs as Tabs,
        TextArea as TextArea,
    )
