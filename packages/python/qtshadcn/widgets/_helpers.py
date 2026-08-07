"""Internal helpers shared by qtshadcn widgets."""

from __future__ import annotations

from typing import Any, Iterable


def initialize_component(widget: Any, component: str) -> None:
    widget.setObjectName(f"qtshadcn-{component}")
    widget.setProperty("qtshadcn_component", component)


def refresh_style(widget: Any) -> None:
    style = widget.style()
    if style is not None:
        style.unpolish(widget)
        style.polish(widget)
    widget.update()


def set_choice_property(
    widget: Any,
    attribute: str,
    property_name: str,
    value: str,
    choices: Iterable[str],
) -> None:
    allowed = tuple(choices)
    if value not in allowed:
        raise ValueError(f"{property_name} must be one of {allowed}, got {value!r}")
    # Do not call QObject.setProperty here: for a declared Qt property that
    # would invoke its setter again and recurse.  QSS can read the declared
    # property through Qt's meta-object system.
    setattr(widget, attribute, value)
    refresh_style(widget)
