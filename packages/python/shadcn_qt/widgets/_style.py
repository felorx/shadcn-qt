"""Internal visual helpers for the classic new-york widget profile."""

from __future__ import annotations

from typing import Any, Optional

from shadcn_qt import _qt

QtCore, QtGui, QtWidgets = _qt.qt_modules()


def _palette_role(name: str) -> Any:
    palette = QtGui.QPalette
    direct = getattr(palette, name, None)
    if direct is not None:
        return direct
    return getattr(palette.ColorRole, name)


def semantic_color(
    widget: Any,
    name: str,
    *,
    fallback_role: str = "WindowText",
) -> Any:
    """Return an active semantic theme color for custom-painted controls."""

    app = QtWidgets.QApplication.instance()
    value = app.property(f"shadcn_qt_color_{name}") if app is not None else None
    color = QtGui.QColor(str(value)) if value else QtGui.QColor()
    if color.isValid():
        return color
    return widget.palette().color(_palette_role(fallback_role))


def with_alpha(color: Any, alpha: int) -> Any:
    result = QtGui.QColor(color)
    result.setAlpha(max(0, min(255, int(alpha))))
    return result


def enable_antialiasing(painter: Any) -> None:
    hint = getattr(QtGui.QPainter, "Antialiasing", None)
    if hint is None:
        hint = QtGui.QPainter.RenderHint.Antialiasing
    painter.setRenderHint(hint, True)


def install_shadow(widget: Any, level: str = "sm") -> None:
    """Install a Qt approximation of the new-york elevation presets."""

    presets = {
        "xs": (4.0, 0.0, 1.0, 36),
        "sm": (8.0, 0.0, 2.0, 42),
        "md": (16.0, 0.0, 5.0, 52),
        "lg": (28.0, 0.0, 10.0, 64),
    }
    blur, x_offset, y_offset, alpha = presets[level]
    effect = QtWidgets.QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(x_offset, y_offset)
    effect.setColor(QtGui.QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(effect)
    widget._shadcn_qt_shadow = effect


def clear_graphics_effect(widget: Any) -> None:
    effect = widget.graphicsEffect()
    if effect is not None:
        widget.setGraphicsEffect(None)
    widget._shadcn_qt_shadow = None


def animate_window_opacity(
    widget: Any,
    *,
    start: float = 0.0,
    end: float = 1.0,
    duration: int = 150,
) -> Optional[Any]:
    """Fade a top-level popup without replacing its shadow effect."""

    if not widget.isWindow():
        return None
    widget.setWindowOpacity(start)
    animation = QtCore.QPropertyAnimation(widget, b"windowOpacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(start)
    animation.setEndValue(end)
    easing = getattr(QtCore.QEasingCurve, "OutCubic", None)
    if easing is None:
        easing = QtCore.QEasingCurve.Type.OutCubic
    animation.setEasingCurve(easing)
    animation.start()
    widget._shadcn_qt_opacity_animation = animation
    return animation


def text_width(metrics: Any, text: str) -> int:
    advance = getattr(metrics, "horizontalAdvance", None)
    return advance(text) if callable(advance) else metrics.width(text)


__all__ = [
    "animate_window_opacity",
    "clear_graphics_effect",
    "enable_antialiasing",
    "install_shadow",
    "semantic_color",
    "text_width",
    "with_alpha",
]
