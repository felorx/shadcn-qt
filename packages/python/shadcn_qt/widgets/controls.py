"""Additional shadcn-aligned Qt primitives."""

from __future__ import annotations

from typing import Any, Optional, Union

from shadcn_qt import _qt
from shadcn_qt.widgets._helpers import (
    initialize_component,
    refresh_style,
    set_choice_property,
)
from shadcn_qt.widgets._icons import _install_combo_box_chevron
from shadcn_qt.widgets._style import (
    clear_graphics_effect,
    enable_antialiasing,
    handle_combo_mouse_press,
    handle_combo_mouse_release,
    install_shadow,
    position_combo_popup,
    semantic_color,
    style_combo_popup,
    text_width,
    with_alpha,
)

QtCore, QtGui, QtWidgets = _qt.qt_modules()

_CHOICE_EDGE_INSET = 3
_CHOICE_SHADOW_OFFSET_Y = 1.0
# Three low-opacity contours approximate Tailwind's shadow-xs blur without
# applying a QGraphicsEffect to the label text. Their combined alpha is 13/255
# (about 5%), matching ``0 1px 2px rgb(0 0 0 / 0.05)``.
_CHOICE_SHADOW_LAYERS = ((1.0, 3), (0.5, 4), (0.0, 6))


def _alignment_flag(name: str) -> Any:
    value = getattr(QtCore.Qt, name, None)
    if value is not None:
        return value
    return getattr(QtCore.Qt.AlignmentFlag, name)


def _qt_enum(name: str, group: str) -> Any:
    value = getattr(QtCore.Qt, name, None)
    if value is not None:
        return value
    return getattr(getattr(QtCore.Qt, group), name)


def _choice_size_hint(widget: Any, indicator_width: int) -> Any:
    metrics = widget.fontMetrics()
    label_width = text_width(metrics, widget.text())
    gap = 8 if widget.text() else 0
    return QtCore.QSize(
        _CHOICE_EDGE_INSET + indicator_width + gap + label_width,
        max(24, metrics.height()),
    )


def _choice_geometry(widget: Any, indicator_size: int) -> tuple[Any, Any]:
    y = (widget.height() - indicator_size) / 2
    rtl = widget.layoutDirection() == getattr(
        QtCore.Qt,
        "RightToLeft",
        getattr(getattr(QtCore.Qt, "LayoutDirection", object), "RightToLeft", None),
    )
    x = (
        widget.width() - indicator_size - _CHOICE_EDGE_INSET
        if rtl
        else _CHOICE_EDGE_INSET
    )
    indicator = QtCore.QRectF(x, y, indicator_size, indicator_size)
    if rtl:
        text_rect = QtCore.QRectF(0, 0, max(0, x - 8), widget.height())
    else:
        text_rect = QtCore.QRectF(
            x + indicator_size + 8,
            0,
            max(0, widget.width() - x - indicator_size - 8),
            widget.height(),
        )
    return indicator, text_rect


def _draw_choice_text(widget: Any, painter: Any, rect: Any) -> None:
    foreground = semantic_color(widget, "foreground")
    if not widget.isEnabled():
        foreground = with_alpha(foreground, 128)
    painter.setPen(foreground)
    flags = _alignment_flag("AlignVCenter") | _alignment_flag("AlignLeft")
    painter.drawText(rect, int(flags), widget.text())


def _draw_choice_shadow(
    painter: Any,
    indicator: Any,
    *,
    radio: bool,
    enabled: bool,
) -> None:
    painter.save()
    painter.setPen(_qt_enum("NoPen", "PenStyle"))
    for expansion, alpha in _CHOICE_SHADOW_LAYERS:
        if not enabled:
            alpha = round(alpha * 0.5)
        painter.setBrush(with_alpha(QtGui.QColor(0, 0, 0), alpha))
        shadow_rect = indicator.adjusted(
            -expansion,
            -expansion,
            expansion,
            expansion,
        ).translated(0, _CHOICE_SHADOW_OFFSET_Y)
        if radio:
            painter.drawEllipse(shadow_rect)
        else:
            painter.drawRoundedRect(
                shadow_rect,
                3.0 + expansion,
                3.0 + expansion,
            )
    painter.restore()


def _text_parent(text: Any, parent: Optional[Any]) -> tuple[str, Optional[Any]]:
    if isinstance(text, QtWidgets.QWidget) and parent is None:
        return "", text
    return str(text), parent


class Label(QtWidgets.QLabel):
    VARIANTS = ("default", "muted", "lead", "large", "small", "destructive")

    def __init__(
        self,
        text: Union[str, Any] = "",
        parent: Optional[Any] = None,
        *,
        variant: str = "default",
    ) -> None:
        text, parent = _text_parent(text, parent)
        super().__init__(text, parent)
        initialize_component(self, "label")
        self._variant = "default"
        self.set_variant(variant)

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, value: str) -> None:
        set_choice_property(self, "_variant", "variant", value, self.VARIANTS)

    getVariant = get_variant
    setVariant = set_variant
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)


class TextArea(QtWidgets.QPlainTextEdit):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "textarea")
        self._invalid = False
        self.setMinimumHeight(60)
        install_shadow(self, "xs")

    def is_invalid(self) -> bool:
        return self._invalid

    def set_invalid(self, value: bool) -> None:
        self._invalid = bool(value)
        refresh_style(self)

    isInvalid = is_invalid
    setInvalid = set_invalid
    invalid = _qt.qt_property(bool, fget=is_invalid, fset=set_invalid)


class Checkbox(QtWidgets.QCheckBox):
    def __init__(
        self, text: Union[str, Any] = "", parent: Optional[Any] = None
    ) -> None:
        text, parent = _text_parent(text, parent)
        super().__init__(text, parent)
        initialize_component(self, "checkbox")
        self.setMouseTracking(True)

    def sizeHint(self) -> Any:
        return _choice_size_hint(self, 16)

    def paintEvent(self, event: Any) -> None:
        del event
        painter = QtGui.QPainter(self)
        enable_antialiasing(painter)
        indicator, text_rect = _choice_geometry(self, 16)
        primary = semantic_color(self, "primary", fallback_role="Highlight")
        background = semantic_color(self, "background", fallback_role="Window")
        border = primary
        if not self.isEnabled():
            border = with_alpha(border, 128)
        if self.hasFocus():
            painter.setBrush(_qt_enum("NoBrush", "BrushStyle"))
            painter.setPen(QtGui.QPen(semantic_color(self, "ring"), 1))
            painter.drawRoundedRect(
                indicator.adjusted(-1.5, -1.5, 1.5, 1.5), 5, 5
            )
        _draw_choice_shadow(
            painter,
            indicator,
            radio=False,
            enabled=self.isEnabled(),
        )
        painter.setPen(QtGui.QPen(border, 1))
        painter.setBrush(primary if self.isChecked() else background)
        painter.drawRoundedRect(indicator, 3, 3)
        if self.isChecked():
            foreground = semantic_color(
                self, "primaryForeground", fallback_role="HighlightedText"
            )
            pen = QtGui.QPen(foreground, 1.8)
            pen.setCapStyle(_qt_enum("RoundCap", "PenCapStyle"))
            pen.setJoinStyle(_qt_enum("RoundJoin", "PenJoinStyle"))
            painter.setPen(pen)
            path = QtGui.QPainterPath()
            path.moveTo(indicator.left() + 3.5, indicator.center().y())
            path.lineTo(indicator.left() + 6.8, indicator.bottom() - 3.8)
            path.lineTo(indicator.right() - 3.2, indicator.top() + 3.8)
            painter.drawPath(path)
        _draw_choice_text(self, painter, text_rect)


class RadioButton(QtWidgets.QRadioButton):
    def __init__(
        self, text: Union[str, Any] = "", parent: Optional[Any] = None
    ) -> None:
        text, parent = _text_parent(text, parent)
        super().__init__(text, parent)
        initialize_component(self, "radio")
        self.setMouseTracking(True)

    def sizeHint(self) -> Any:
        return _choice_size_hint(self, 16)

    def paintEvent(self, event: Any) -> None:
        del event
        painter = QtGui.QPainter(self)
        enable_antialiasing(painter)
        indicator, text_rect = _choice_geometry(self, 16)
        primary = semantic_color(self, "primary", fallback_role="Highlight")
        background = semantic_color(self, "background", fallback_role="Window")
        border = primary if self.isEnabled() else with_alpha(primary, 128)
        if self.hasFocus():
            painter.setBrush(_qt_enum("NoBrush", "BrushStyle"))
            painter.setPen(QtGui.QPen(semantic_color(self, "ring"), 1))
            painter.drawEllipse(indicator.adjusted(-1.5, -1.5, 1.5, 1.5))
        _draw_choice_shadow(
            painter,
            indicator,
            radio=True,
            enabled=self.isEnabled(),
        )
        painter.setPen(QtGui.QPen(border, 1))
        painter.setBrush(background)
        painter.drawEllipse(indicator)
        if self.isChecked():
            painter.setPen(_qt_enum("NoPen", "PenStyle"))
            painter.setBrush(primary)
            painter.drawEllipse(indicator.adjusted(4.5, 4.5, -4.5, -4.5))
        _draw_choice_text(self, painter, text_rect)


class Switch(QtWidgets.QCheckBox):
    def __init__(
        self, text: Union[str, Any] = "", parent: Optional[Any] = None
    ) -> None:
        text, parent = _text_parent(text, parent)
        super().__init__(text, parent)
        initialize_component(self, "switch")
        self._thumb_position = 1.0 if self.isChecked() else 0.0
        self._animation = QtCore.QVariantAnimation(self)
        self._animation.setDuration(150)
        easing = getattr(QtCore.QEasingCurve, "OutCubic", None)
        if easing is None:
            easing = QtCore.QEasingCurve.Type.OutCubic
        self._animation.setEasingCurve(easing)
        self._animation.valueChanged.connect(self._set_thumb_position)
        self.toggled.connect(self._animate_thumb)
        self.setMouseTracking(True)

    def sizeHint(self) -> Any:
        return _choice_size_hint(self, 36)

    def _set_thumb_position(self, value: Any) -> None:
        self._thumb_position = float(value)
        self.update()

    def _animate_thumb(self, checked: bool) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._thumb_position)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()

    def paintEvent(self, event: Any) -> None:
        del event
        painter = QtGui.QPainter(self)
        enable_antialiasing(painter)
        track, text_rect = _choice_geometry(self, 36)
        track.setHeight(20)
        track.moveTop((self.height() - 20) / 2)
        primary = semantic_color(self, "primary", fallback_role="Highlight")
        input_color = semantic_color(self, "input", fallback_role="Button")
        background = semantic_color(self, "background", fallback_role="Window")
        if not self.isEnabled():
            primary = with_alpha(primary, 128)
            input_color = with_alpha(input_color, 128)
        if self.hasFocus():
            painter.setBrush(_qt_enum("NoBrush", "BrushStyle"))
            painter.setPen(QtGui.QPen(semantic_color(self, "ring"), 2))
            painter.drawRoundedRect(
                track.adjusted(-1.5, -1.5, 1.5, 1.5), 12, 12
            )
        painter.setPen(_qt_enum("NoPen", "PenStyle"))
        painter.setBrush(with_alpha(QtGui.QColor(0, 0, 0), 30))
        painter.drawRoundedRect(track.translated(0, 1), 10, 10)
        painter.setBrush(primary if self.isChecked() else input_color)
        painter.drawRoundedRect(track, 10, 10)
        thumb_x = track.left() + 2 + (16 * self._thumb_position)
        thumb = QtCore.QRectF(thumb_x, track.top() + 2, 16, 16)
        painter.setBrush(with_alpha(QtGui.QColor(0, 0, 0), 42))
        painter.drawEllipse(thumb.translated(0, 1))
        painter.setBrush(background)
        painter.drawEllipse(thumb)
        _draw_choice_text(self, painter, text_rect)


class Select(QtWidgets.QComboBox):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "select")
        self.setFixedHeight(36)
        install_shadow(self, "xs")
        _install_combo_box_chevron(self, "chevron-down")

    def showPopup(self) -> None:
        popup = style_combo_popup(self)
        super().showPopup()
        position_combo_popup(self, popup)

    def mousePressEvent(self, event: Any) -> None:
        if not handle_combo_mouse_press(self, event, trigger_only=False):
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:
        if not handle_combo_mouse_release(self, event):
            super().mouseReleaseEvent(event)


class Slider(QtWidgets.QSlider):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "slider")
        horizontal = getattr(QtCore.Qt, "Horizontal", None)
        if horizontal is None:
            horizontal = QtCore.Qt.Orientation.Horizontal
        self.setOrientation(horizontal)
        self.setMinimumHeight(20)


class Progress(QtWidgets.QProgressBar):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "progress")
        self.setTextVisible(False)
        self.setFixedHeight(8)


class Tabs(QtWidgets.QTabWidget):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "tabs")


class Badge(QtWidgets.QLabel):
    VARIANTS = ("default", "secondary", "outline", "destructive")

    def __init__(
        self,
        text: Union[str, Any] = "Badge",
        parent: Optional[Any] = None,
        *,
        variant: str = "default",
    ) -> None:
        text, parent = _text_parent(text, parent)
        super().__init__(text, parent)
        initialize_component(self, "badge")
        self._variant = "default"
        self.set_variant(variant)

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, value: str) -> None:
        set_choice_property(self, "_variant", "variant", value, self.VARIANTS)
        if value in {"default", "destructive"}:
            install_shadow(self, "xs")
        else:
            clear_graphics_effect(self)

    getVariant = get_variant
    setVariant = set_variant
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)


class Alert(QtWidgets.QFrame):
    VARIANTS = ("default", "destructive")

    def __init__(
        self, parent: Optional[Any] = None, *, variant: str = "default"
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "alert")
        self._variant = "default"
        self.set_variant(variant)

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, value: str) -> None:
        set_choice_property(self, "_variant", "variant", value, self.VARIANTS)

    getVariant = get_variant
    setVariant = set_variant
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)


class Separator(QtWidgets.QFrame):
    ORIENTATIONS = ("horizontal", "vertical")

    def __init__(
        self, parent: Optional[Any] = None, *, orientation: str = "horizontal"
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "separator")
        self._orientation_name = "horizontal"
        self.set_orientation(orientation)

    def get_orientation(self) -> str:
        return self._orientation_name

    def set_orientation(self, value: str) -> None:
        if value not in self.ORIENTATIONS:
            raise ValueError(
                f"orientation must be one of {self.ORIENTATIONS}, got {value!r}"
            )
        self._orientation_name = value
        frame = QtWidgets.QFrame
        if value == "horizontal":
            shape = getattr(frame, "HLine", None)
            if shape is None:
                shape = frame.Shape.HLine
            self.setFrameShape(shape)
            self.setFixedHeight(1)
            self.setMaximumWidth(16777215)
        else:
            shape = getattr(frame, "VLine", None)
            if shape is None:
                shape = frame.Shape.VLine
            self.setFrameShape(shape)
            self.setFixedWidth(1)
            self.setMaximumHeight(16777215)
        refresh_style(self)

    getOrientation = get_orientation
    setOrientation = set_orientation
    orientation = _qt.qt_property(str, fget=get_orientation, fset=set_orientation)


__all__ = [
    "Alert",
    "Badge",
    "Checkbox",
    "Label",
    "Progress",
    "RadioButton",
    "Select",
    "Separator",
    "Slider",
    "Switch",
    "Tabs",
    "TextArea",
]
