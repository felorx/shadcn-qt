"""Global and user-defined shadcn-qt themes."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Union

from shadcn_qt import _qt
from shadcn_qt._generated.colors import FONT, RADIUS, THEMES
from shadcn_qt._radius import RadiusBase, derive_radius
from shadcn_qt._stylesheet import render_stylesheet

ThemeLike = Union[str, "Theme", Mapping[str, Any]]
ThemeMode = Literal["light", "dark"]
STYLE_PROFILE = "new-york"
BASE_COLOR = "zinc"

_REQUIRED_COLORS = frozenset(
    {
        "background",
        "foreground",
        "card",
        "cardForeground",
        "popover",
        "popoverForeground",
        "primary",
        "primaryForeground",
        "secondary",
        "secondaryForeground",
        "muted",
        "mutedForeground",
        "accent",
        "accentForeground",
        "destructive",
        "destructiveForeground",
        "border",
        "input",
        "ring",
    }
)


@dataclass(frozen=True)
class Theme:
    """A complete semantic theme independent of any Qt binding."""

    name: str
    colors: Mapping[str, str]
    radius: Mapping[str, str] = field(default_factory=dict)
    font: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        missing = sorted(_REQUIRED_COLORS.difference(self.colors))
        if missing:
            raise ValueError(
                f"Theme {self.name!r} is missing colors: {', '.join(missing)}"
            )
        object.__setattr__(self, "colors", dict(self.colors))
        object.__setattr__(self, "radius", dict(self.radius))
        object.__setattr__(self, "font", dict(self.font))

    def with_overrides(
        self,
        *,
        name: Optional[str] = None,
        colors: Optional[Mapping[str, str]] = None,
        radius_base: Optional[RadiusBase] = None,
        radius: Optional[Mapping[str, str]] = None,
        font: Optional[Mapping[str, str]] = None,
    ) -> "Theme":
        return Theme(
            name or self.name,
            {**self.colors, **(colors or {})},
            {
                **self.radius,
                **(derive_radius(radius_base) if radius_base is not None else {}),
                **(radius or {}),
            },
            {**self.font, **(font or {})},
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "colors": dict(self.colors),
            "radius": dict(self.radius),
            "font": dict(self.font),
        }


_REGISTRY: Dict[str, Theme] = {
    name: Theme(name, colors, RADIUS, FONT) for name, colors in THEMES.items()
}


@dataclass
class ThemeConfig:
    """Process-wide defaults used by :func:`apply_theme`."""

    theme: ThemeLike = "light"
    colors: Dict[str, str] = field(default_factory=dict)
    radius_base: Optional[RadiusBase] = None
    radius: Dict[str, str] = field(default_factory=dict)
    font: Dict[str, str] = field(default_factory=dict)
    extra_qss: str = ""
    apply_palette: bool = True


_CONFIG = ThemeConfig()


def available_themes() -> Iterable[str]:
    return tuple(_REGISTRY)


def create_theme(
    name: str,
    *,
    base: ThemeLike = "light",
    colors: Optional[Mapping[str, str]] = None,
    radius_base: Optional[RadiusBase] = None,
    radius: Optional[Mapping[str, str]] = None,
    font: Optional[Mapping[str, str]] = None,
) -> Theme:
    """Create a complete theme by overriding semantic tokens from ``base``."""

    return resolve_theme(base).with_overrides(
        name=name,
        colors=colors,
        radius_base=radius_base,
        radius=radius,
        font=font,
    )


def resolve_theme(theme: ThemeLike) -> Theme:
    if isinstance(theme, Theme):
        return theme
    if isinstance(theme, str):
        try:
            return _REGISTRY[theme]
        except KeyError as exc:
            raise ValueError(
                f"Unknown theme {theme!r}; available: {', '.join(_REGISTRY)}"
            ) from exc
    if isinstance(theme, Mapping):
        name = str(theme.get("name", "custom"))
        base = theme.get("base", "light")
        if "themes" in theme:
            palettes = theme["themes"]
            if not isinstance(palettes, Mapping) or not palettes:
                raise ValueError(
                    "A theme file's 'themes' value must be a non-empty mapping."
                )
            selected = (
                palettes.get(name)
                or palettes.get("light")
                or next(iter(palettes.values()))
            )
            return create_theme(
                name,
                base=base,
                colors=selected,
                radius_base=theme.get("radius_base", theme.get("radiusBase")),
                radius=theme.get("radius"),
                font=theme.get("font"),
            )
        return create_theme(
            name,
            base=base,
            colors=theme.get("colors"),
            radius_base=theme.get("radius_base", theme.get("radiusBase")),
            radius=theme.get("radius"),
            font=theme.get("font"),
        )
    raise TypeError(f"Unsupported theme value: {type(theme).__name__}")


def register_theme(theme: Theme, *, replace: bool = False) -> None:
    if theme.name in _REGISTRY and not replace:
        raise ValueError(f"Theme {theme.name!r} is already registered.")
    _REGISTRY[theme.name] = theme


def load_theme(path: Union[str, Path], *, name: Optional[str] = None) -> Theme:
    """Load a custom JSON theme and merge missing values from its ``base``."""

    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Theme file {source} must contain a JSON object.")
    if name is not None:
        data["name"] = name
    elif "name" not in data:
        data["name"] = source.stem
    return resolve_theme(data)


def configure(
    *,
    theme: Optional[ThemeLike] = None,
    colors: Optional[Mapping[str, str]] = None,
    radius_base: Optional[RadiusBase] = None,
    radius: Optional[Mapping[str, str]] = None,
    font: Optional[Mapping[str, str]] = None,
    extra_qss: Optional[str] = None,
    apply_palette: Optional[bool] = None,
    app: Any = None,
) -> ThemeConfig:
    """Set global defaults, optionally applying them to a QApplication now."""

    if theme is not None:
        _CONFIG.theme = theme
    if colors is not None:
        _CONFIG.colors = dict(colors)
    if radius_base is not None:
        # Validate eagerly so configuration errors are raised at the call site.
        derive_radius(radius_base)
        _CONFIG.radius_base = radius_base
    if radius is not None:
        _CONFIG.radius = dict(radius)
    if font is not None:
        _CONFIG.font = dict(font)
    if extra_qss is not None:
        _CONFIG.extra_qss = extra_qss
    if apply_palette is not None:
        _CONFIG.apply_palette = apply_palette
    if app is not None:
        apply_theme(app)
    return _CONFIG


def current_theme() -> Theme:
    return resolve_theme(_CONFIG.theme).with_overrides(
        colors=_CONFIG.colors,
        radius_base=_CONFIG.radius_base,
        radius=_CONFIG.radius,
        font=_CONFIG.font,
    )


def theme_stylesheet(
    theme: Optional[ThemeLike] = None,
    *,
    radius_base: Optional[RadiusBase] = None,
    radius: Optional[Mapping[str, str]] = None,
    extra_qss: str = "",
) -> str:
    resolved = current_theme() if theme is None else resolve_theme(theme)
    resolved = resolved.with_overrides(radius_base=radius_base, radius=radius)
    qss = render_stylesheet(resolved.colors, resolved.radius, resolved.font)
    additions = "\n".join(part for part in (_CONFIG.extra_qss, extra_qss) if part)
    return qss + ("\n/* User overrides */\n" + additions if additions else "")


def apply_theme(
    app: Any = None,
    mode: Optional[ThemeLike] = None,
    *,
    theme: Optional[ThemeLike] = None,
    colors: Optional[Mapping[str, str]] = None,
    radius_base: Optional[RadiusBase] = None,
    radius: Optional[Mapping[str, str]] = None,
    font: Optional[Mapping[str, str]] = None,
    extra_qss: str = "",
    apply_palette: Optional[bool] = None,
) -> Theme:
    """Apply a built-in or custom theme to the application.

    Pass an application explicitly with ``apply_theme(app, "dark")``, or use
    ``apply_theme("dark")`` with the current QApplication.
    """

    if isinstance(app, (str, Theme, Mapping)) and mode is None and theme is None:
        mode, app = app, None
    selected = theme if theme is not None else mode
    if selected is None:
        base = current_theme()
    else:
        base = resolve_theme(selected).with_overrides(
            colors=_CONFIG.colors,
            radius_base=_CONFIG.radius_base,
            radius=_CONFIG.radius,
            font=_CONFIG.font,
        )
    resolved = base.with_overrides(
        colors=colors,
        radius_base=radius_base,
        radius=radius,
        font=font,
    )

    _, _, widgets = _qt.qt_modules()
    if app is None:
        app = widgets.QApplication.instance()
    if app is None:
        raise RuntimeError(
            "No QApplication instance; create QApplication before apply_theme()."
        )

    app.setProperty("shadcn_qt_style", STYLE_PROFILE)
    app.setProperty("shadcn_qt_base_color", BASE_COLOR)
    for color_name, color_value in resolved.colors.items():
        app.setProperty(f"shadcn_qt_color_{color_name}", color_value)
    for radius_name, fallback in RADIUS.items():
        app.setProperty(
            f"shadcn_qt_radius_{radius_name}",
            resolved.radius.get(radius_name, fallback),
        )

    app.setStyleSheet(
        render_stylesheet(resolved.colors, resolved.radius, resolved.font)
        + (
            "\n/* Global overrides */\n" + _CONFIG.extra_qss
            if _CONFIG.extra_qss
            else ""
        )
        + ("\n/* User overrides */\n" + extra_qss if extra_qss else "")
    )
    app.setProperty("shadcn_qt_theme", resolved.name)
    should_apply_palette = (
        _CONFIG.apply_palette if apply_palette is None else apply_palette
    )
    if should_apply_palette:
        apply_palette_from_tokens(app, resolved)
    return resolved


def apply_palette_from_tokens(
    app: Any = None, mode: Optional[ThemeLike] = None
) -> None:
    """Apply important semantic colors through QPalette as well as QSS."""

    _, gui, widgets = _qt.qt_modules()
    if app is None:
        app = widgets.QApplication.instance()
    if app is None:
        raise RuntimeError("No QApplication instance; create QApplication first.")
    resolved = current_theme() if mode is None else resolve_theme(mode)
    c = resolved.colors
    palette_type = gui.QPalette

    def role(name: str) -> Any:
        direct = getattr(palette_type, name, None)
        if direct is not None:
            return direct
        scope = getattr(palette_type, "ColorRole", None)
        return getattr(scope, name, None) if scope is not None else None

    palette = gui.QPalette()
    values = {
        "Window": c["background"],
        "WindowText": c["foreground"],
        "Base": c["background"],
        "AlternateBase": c["muted"],
        "Text": c["foreground"],
        "Button": c["secondary"],
        "ButtonText": c["secondaryForeground"],
        "Highlight": c["primary"],
        "HighlightedText": c["primaryForeground"],
        "ToolTipBase": c["popover"],
        "ToolTipText": c["popoverForeground"],
    }
    for name, value in values.items():
        color_role = role(name)
        if color_role is not None:
            palette.setColor(color_role, gui.QColor(value))
    app.setPalette(palette)


__all__ = [
    "BASE_COLOR",
    "STYLE_PROFILE",
    "Theme",
    "ThemeConfig",
    "ThemeLike",
    "ThemeMode",
    "apply_palette_from_tokens",
    "apply_theme",
    "available_themes",
    "configure",
    "create_theme",
    "current_theme",
    "load_theme",
    "register_theme",
    "resolve_theme",
    "theme_stylesheet",
]
