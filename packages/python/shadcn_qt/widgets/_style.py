"""Internal visual helpers for the classic new-york widget profile."""

from __future__ import annotations

from typing import Any, Optional

from shadcn_qt import _qt
from shadcn_qt._radius import format_radius, radius_pixels

QtCore, QtGui, QtWidgets = _qt.qt_modules()

_DEFAULT_RADIUS = {"sm": 4.0, "md": 6.0, "lg": 8.0, "xl": 12.0}
_COMBO_POPUP_DELEGATE_ATTRIBUTE = "_shadcn_qt_combo_popup_delegate"
_COMBO_POPUP_ITEM_MIN_HEIGHT = 32
_SIZE_HINT_ROLE = getattr(QtCore.Qt, "SizeHintRole", None)
if _SIZE_HINT_ROLE is None:
    _SIZE_HINT_ROLE = QtCore.Qt.ItemDataRole.SizeHintRole


class _ComboPopupSourceDelegate(QtWidgets.QStyledItemDelegate):
    """Expose the normalized Qt delegate through a Python-owned subclass."""


class ComboPopupItemDelegate(QtWidgets.QAbstractItemDelegate):
    """Preserve an existing delegate while enforcing the popup row minimum."""

    def __init__(self, source: Any, parent: Any) -> None:
        super().__init__(parent)
        self.source_delegate = source
        for signal_name in ("commitData", "closeEditor", "sizeHintChanged"):
            source_signal = getattr(source, signal_name, None)
            proxy_signal = getattr(self, signal_name, None)
            if source_signal is None or proxy_signal is None:
                continue
            try:
                source_signal.connect(proxy_signal.emit)
            except (RuntimeError, TypeError):
                pass

    def paint(self, painter: Any, option: Any, index: Any) -> None:
        self.source_delegate.paint(painter, option, index)

    def sizeHint(self, option: Any, index: Any) -> Any:
        hint = QtCore.QSize(self.source_delegate.sizeHint(option, index))
        model_hint = index.data(_SIZE_HINT_ROLE)
        model_height = (
            model_hint.height()
            if isinstance(model_hint, QtCore.QSize) and model_hint.isValid()
            else -1
        )
        hint.setHeight(
            max(
                _COMBO_POPUP_ITEM_MIN_HEIGHT,
                hint.height(),
                model_height,
            )
        )
        return hint

    def createEditor(self, parent: Any, option: Any, index: Any) -> Any:
        return self.source_delegate.createEditor(parent, option, index)

    def destroyEditor(self, editor: Any, index: Any) -> None:
        self.source_delegate.destroyEditor(editor, index)

    def setEditorData(self, editor: Any, index: Any) -> None:
        self.source_delegate.setEditorData(editor, index)

    def setModelData(self, editor: Any, model: Any, index: Any) -> None:
        self.source_delegate.setModelData(editor, model, index)

    def updateEditorGeometry(
        self,
        editor: Any,
        option: Any,
        index: Any,
    ) -> None:
        self.source_delegate.updateEditorGeometry(editor, option, index)

    def editorEvent(
        self,
        event: Any,
        model: Any,
        option: Any,
        index: Any,
    ) -> bool:
        try:
            return self.source_delegate.editorEvent(event, model, option, index)
        except RuntimeError as error:
            # SIP rejects protected calls on delegates constructed in C++.
            # The view still needs the base behavior so popup activation can
            # proceed without allowing the exception to escape into Qt.
            if "protected" not in str(error):
                raise
            return super().editorEvent(event, model, option, index)

    def helpEvent(
        self,
        event: Any,
        view: Any,
        option: Any,
        index: Any,
    ) -> bool:
        try:
            return self.source_delegate.helpEvent(event, view, option, index)
        except RuntimeError as error:
            if "protected" not in str(error):
                raise
            return super().helpEvent(event, view, option, index)

    def eventFilter(self, watched: Any, event: Any) -> bool:
        try:
            return self.source_delegate.eventFilter(watched, event)
        except RuntimeError as error:
            if "protected" not in str(error):
                raise
            return super().eventFilter(watched, event)


def install_combo_popup_delegate(widget: Any) -> Any:
    """Wrap a combo's delegate with the 32px shadcn popup-row contract."""

    view = widget.view()
    delegate = view.itemDelegate()
    if isinstance(delegate, ComboPopupItemDelegate):
        setattr(view, _COMBO_POPUP_DELEGATE_ATTRIBUTE, delegate)
        setattr(
            widget,
            _COMBO_POPUP_DELEGATE_ATTRIBUTE,
            (view, delegate),
        )
        return delegate
    installed = getattr(widget, _COMBO_POPUP_DELEGATE_ATTRIBUTE, None)
    previous = installed[1] if installed is not None else None
    if previous is None:
        previous = getattr(view, _COMBO_POPUP_DELEGATE_ATTRIBUTE, None)
    if previous is not None and previous is not delegate:
        try:
            previous.deleteLater()
        except RuntimeError:
            pass
    source = delegate
    owns_source = type(delegate) is QtWidgets.QAbstractItemDelegate
    if owns_source:
        # Qt exposes its private QComboMenuDelegate through the abstract base
        # wrapper. Its menu-oriented width calculation can exceed the popup,
        # so retain the existing QStyledItemDelegate normalization for this
        # one private implementation. User delegates are always preserved.
        source = _ComboPopupSourceDelegate()
    replacement = ComboPopupItemDelegate(source, view)
    if owns_source:
        source.setParent(replacement)
    view.setItemDelegate(replacement)
    # SIP can otherwise recreate a base-class wrapper and lose Python method
    # overrides even though Qt still owns the C++ objects. Retain the proxy on
    # both wrappers: ordinary combos keep the public wrapper stable, while
    # complex subclasses can recreate it and keep their popup view stable.
    setattr(view, _COMBO_POPUP_DELEGATE_ATTRIBUTE, replacement)
    setattr(
        widget,
        _COMBO_POPUP_DELEGATE_ATTRIBUTE,
        (view, replacement),
    )
    return replacement


def restore_combo_popup_delegate(
    widget: Any,
    view: Any,
    replacement: Any,
    original: Any,
) -> None:
    """Remove an installed row-height proxy without clobbering later changes."""

    if view.itemDelegate() is replacement:
        view.setItemDelegate(original)
    installed = getattr(view, _COMBO_POPUP_DELEGATE_ATTRIBUTE, None)
    if installed is replacement:
        delattr(view, _COMBO_POPUP_DELEGATE_ATTRIBUTE)
    installed = getattr(widget, _COMBO_POPUP_DELEGATE_ATTRIBUTE, None)
    if installed is not None and installed[1] is replacement:
        delattr(widget, _COMBO_POPUP_DELEGATE_ATTRIBUTE)
    try:
        replacement.deleteLater()
    except RuntimeError:
        pass


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


def semantic_radius(
    widget: Any,
    name: str = "md",
    *,
    fallback: Optional[float] = None,
) -> float:
    """Return the active semantic radius for custom-painted geometry."""

    default = _DEFAULT_RADIUS.get(name, 0.0) if fallback is None else fallback
    app = QtWidgets.QApplication.instance()
    value = app.property(f"shadcn_qt_radius_{name}") if app is not None else None
    if value is None:
        return float(default)
    try:
        return radius_pixels(str(value), name=f"radius[{name!r}]")
    except (TypeError, ValueError):
        return float(default)


def semantic_radius_css(widget: Any, name: str = "md") -> str:
    """Return a semantic radius formatted for an inline Qt Style Sheet."""

    return format_radius(semantic_radius(widget, name))


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
    radius = semantic_radius_css(widget, "md")
    popup.setStyleSheet(
        "#shadcnQtComboPopup { "
        f"background: {background}; border: 1px solid {border}; "
        f"border-radius: {radius}; }}"
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
    install_combo_popup_delegate(widget)
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
    "ComboPopupItemDelegate",
    "animate_window_opacity",
    "clear_graphics_effect",
    "enable_antialiasing",
    "handle_combo_mouse_press",
    "handle_combo_mouse_release",
    "install_shadow",
    "install_combo_popup_delegate",
    "position_combo_popup",
    "position_popup_below",
    "restore_combo_popup_delegate",
    "semantic_color",
    "style_combo_popup",
    "text_width",
    "with_alpha",
]
