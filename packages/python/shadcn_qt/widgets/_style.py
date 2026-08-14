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
    """Install a restrained single-layer approximation of new-york shadows."""

    presets = {
        # Qt has one drop-shadow layer per widget, while the web presets use
        # multiple low-opacity layers. Keep the approximation short and light
        # so borders remain crisp instead of acquiring a grey halo.
        "xs": (2.0, 0.0, 1.0, 13),
        "sm": (4.0, 0.0, 1.0, 16),
        "md": (10.0, 0.0, 3.0, 20),
        "lg": (20.0, 0.0, 6.0, 24),
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


def style_combo_popup(widget: Any) -> Any:
    """Give Qt's private combo popup one themed outer border."""

    view = widget.view()
    popup = view.window()
    popup.setObjectName("shadcnQtComboPopup")
    background = semantic_color(widget, "popover").name()
    border = semantic_color(widget, "border").name()
    popup.setStyleSheet(
        "#shadcnQtComboPopup { "
        f"background: {background}; border: 1px solid {border}; "
        "border-radius: 6px; }"
    )
    popup.setFixedWidth(max(1, widget.width()))
    scroll_off = getattr(QtCore.Qt, "ScrollBarAlwaysOff", None)
    elide_right = getattr(QtCore.Qt, "ElideRight", None)
    if scroll_off is None:
        scroll_off = QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    if elide_right is None:
        elide_right = QtCore.Qt.TextElideMode.ElideRight
    view.setHorizontalScrollBarPolicy(scroll_off)
    view.setTextElideMode(elide_right)
    view.setMouseTracking(True)
    delegate = view.itemDelegate()
    if type(delegate) is QtWidgets.QAbstractItemDelegate:
        view.setItemDelegate(QtWidgets.QStyledItemDelegate(view))
    return popup


def position_popup_below(
    widget: Any,
    popup: Any,
    *,
    match_width: bool = False,
) -> Any:
    """Left-align a popup directly below its trigger control."""

    if match_width:
        popup.setFixedWidth(max(1, widget.width()))
    popup.move(widget.mapToGlobal(QtCore.QPoint(0, widget.height())))
    return popup


def position_combo_popup(widget: Any, popup: Any = None) -> Any:
    """Left-align a combo popup below its trigger and match its width."""

    popup = popup or widget.view().window()
    return position_popup_below(widget, popup, match_width=True)


def handle_combo_mouse_press(
    widget: Any,
    event: Any,
    *,
    trigger_only: bool,
) -> bool:
    """Begin a combo click without opening its popup before mouse release."""

    left_button = getattr(QtCore.Qt, "LeftButton", None)
    if left_button is None:
        left_button = QtCore.Qt.MouseButton.LeftButton
    if event.button() != left_button:
        return False
    if trigger_only:
        position = getattr(event, "position", None)
        point = position().toPoint() if callable(position) else event.pos()
        controller = getattr(widget, "_shadcn_qt_combo_chevron", None)
        if controller is None or not controller.glyph.geometry().contains(point):
            return False
    widget._shadcn_qt_combo_click_pending = True
    widget.setFocus()
    event.accept()
    return True


def handle_combo_mouse_release(widget: Any, event: Any) -> bool:
    """Open a pending combo popup after Cocoa has delivered mouse release."""

    if not getattr(widget, "_shadcn_qt_combo_click_pending", False):
        return False
    widget._shadcn_qt_combo_click_pending = False
    left_button = getattr(QtCore.Qt, "LeftButton", None)
    if left_button is None:
        left_button = QtCore.Qt.MouseButton.LeftButton
    if event.button() != left_button:
        return False
    position = getattr(event, "position", None)
    point = position().toPoint() if callable(position) else event.pos()
    if widget.rect().contains(point):
        widget.showPopup()
    event.accept()
    return True


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
    "handle_combo_mouse_press",
    "handle_combo_mouse_release",
    "install_shadow",
    "position_combo_popup",
    "position_popup_below",
    "semantic_color",
    "style_combo_popup",
    "text_width",
    "with_alpha",
]
