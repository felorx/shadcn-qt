"""qtshadcn — shadcn-aligned Qt widgets and customizable themes."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from qtshadcn._qt import app_exec, detect_binding
from qtshadcn.designer.loader import load_ui
from qtshadcn.native import (
    adopt_native_widgets,
    disable_native_widget_styling,
    enable_native_widget_styling,
)
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
        "Accordion",
        "Alert",
        "AlertDialog",
        "AspectRatio",
        "Attachment",
        "Avatar",
        "Badge",
        "Breadcrumb",
        "Bubble",
        "Button",
        "ButtonGroup",
        "Calendar",
        "Card",
        "Carousel",
        "Chart",
        "Checkbox",
        "Collapsible",
        "Combobox",
        "Command",
        "ContextMenu",
        "DataTable",
        "DatePicker",
        "Dialog",
        "Direction",
        "Drawer",
        "DropdownMenu",
        "Empty",
        "Field",
        "HoverCard",
        "Input",
        "InputGroup",
        "InputOTP",
        "Item",
        "Kbd",
        "Label",
        "Marker",
        "Menubar",
        "Message",
        "MessageScroller",
        "NativeSelect",
        "NavigationMenu",
        "Pagination",
        "Popover",
        "Progress",
        "RadioButton",
        "RadioGroup",
        "Resizable",
        "ScrollArea",
        "Select",
        "Separator",
        "Sheet",
        "Sidebar",
        "Slider",
        "Skeleton",
        "Sonner",
        "Spinner",
        "Switch",
        "Table",
        "Tabs",
        "TextArea",
        "Toast",
        "Toggle",
        "ToggleGroup",
        "Tooltip",
        "Typography",
    }
)

__all__ = sorted(_WIDGET_NAMES) + [
    "Theme",
    "ThemeConfig",
    "ThemeMode",
    "apply_palette_from_tokens",
    "apply_theme",
    "app_exec",
    "adopt_native_widgets",
    "available_themes",
    "configure",
    "create_theme",
    "current_theme",
    "detect_binding",
    "disable_native_widget_styling",
    "enable_native_widget_styling",
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
    from qtshadcn.widgets import *  # noqa: F403
