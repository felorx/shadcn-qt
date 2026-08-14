"""Font-independent vector icon primitives used by shadcn components."""

from __future__ import annotations

from typing import Any, Optional

from shadcn_qt import _qt
from shadcn_qt.widgets._style import (
    enable_antialiasing,
    semantic_color,
    with_alpha,
)
from shadcn_qt.widgets.button import Button

QtCore, QtGui, QtWidgets = _qt.qt_modules()


def _event_type(name: str) -> Any:
    value = getattr(QtCore.QEvent, name, None)
    return value if value is not None else getattr(QtCore.QEvent.Type, name)


def _vector_icon_path(rect: Any, icon_name: str) -> Any:
    """Return a small Lucide-style path centered exactly within ``rect``."""

    center = QtCore.QRectF(rect).center()
    path = QtGui.QPainterPath()
    if icon_name == "chevron-left":
        path.moveTo(center.x() + 2.0, center.y() - 4.0)
        path.lineTo(center.x() - 2.0, center.y())
        path.lineTo(center.x() + 2.0, center.y() + 4.0)
    elif icon_name == "chevron-right":
        path.moveTo(center.x() - 2.0, center.y() - 4.0)
        path.lineTo(center.x() + 2.0, center.y())
        path.lineTo(center.x() - 2.0, center.y() + 4.0)
    elif icon_name == "chevron-up":
        path.moveTo(center.x() - 4.0, center.y() + 2.0)
        path.lineTo(center.x(), center.y() - 2.0)
        path.lineTo(center.x() + 4.0, center.y() + 2.0)
    elif icon_name == "chevron-down":
        path.moveTo(center.x() - 4.0, center.y() - 2.0)
        path.lineTo(center.x(), center.y() + 2.0)
        path.lineTo(center.x() + 4.0, center.y() - 2.0)
    elif icon_name == "chevrons-up-down":
        path.moveTo(center.x() - 3.0, center.y() - 2.0)
        path.lineTo(center.x(), center.y() - 5.0)
        path.lineTo(center.x() + 3.0, center.y() - 2.0)
        path.moveTo(center.x() - 3.0, center.y() + 2.0)
        path.lineTo(center.x(), center.y() + 5.0)
        path.lineTo(center.x() + 3.0, center.y() + 2.0)
    elif icon_name == "close":
        path.moveTo(center.x() - 3.5, center.y() - 3.5)
        path.lineTo(center.x() + 3.5, center.y() + 3.5)
        path.moveTo(center.x() + 3.5, center.y() - 3.5)
        path.lineTo(center.x() - 3.5, center.y() + 3.5)
    else:
        raise ValueError(f"unsupported vector icon: {icon_name}")
    return path


def _paint_vector_icon(
    widget: Any,
    painter: Any,
    icon_name: str,
    *,
    rect: Optional[Any] = None,
    color_name: str = "foreground",
) -> None:
    enable_antialiasing(painter)
    color = semantic_color(widget, color_name)
    if not widget.isEnabled():
        color = with_alpha(color, 128)
    pen = QtGui.QPen(color, 1.5)
    cap = getattr(QtCore.Qt, "RoundCap", None)
    join = getattr(QtCore.Qt, "RoundJoin", None)
    if cap is None:
        cap = QtCore.Qt.PenCapStyle.RoundCap
        join = QtCore.Qt.PenJoinStyle.RoundJoin
    pen.setCapStyle(cap)
    pen.setJoinStyle(join)
    painter.setPen(pen)
    target_rect = widget.rect() if rect is None else rect
    painter.drawPath(_vector_icon_path(target_rect, icon_name))


class _VectorIconButton(Button):
    def __init__(
        self,
        icon_name: str,
        parent: Optional[Any] = None,
        *,
        accessible_name: str = "",
        variant: str = "ghost",
        size: str = "icon",
    ) -> None:
        super().__init__("", parent, variant=variant, size=size)
        self._icon_name = icon_name
        if accessible_name:
            self.setAccessibleName(accessible_name)

    def _icon_path(self) -> Any:
        return _vector_icon_path(self.rect(), self._icon_name)

    def paintEvent(self, event: Any) -> None:
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        _paint_vector_icon(self, painter, self._icon_name)


class _VectorIconGlyph(QtWidgets.QWidget):
    def __init__(
        self,
        icon_name: str,
        parent: Any,
        *,
        color_name: str = "mutedForeground",
    ) -> None:
        super().__init__(parent)
        self._icon_name = icon_name
        self._color_name = color_name
        transparent = getattr(QtCore.Qt, "WA_TransparentForMouseEvents", None)
        if transparent is None:
            transparent = QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents
        self.setAttribute(transparent, True)

    def _icon_path(self) -> Any:
        return _vector_icon_path(self.rect(), self._icon_name)

    def paintEvent(self, event: Any) -> None:
        del event
        painter = QtGui.QPainter(self)
        _paint_vector_icon(
            self,
            painter,
            self._icon_name,
            color_name=self._color_name,
        )


class _ComboBoxChevronController(QtCore.QObject):
    def __init__(self, widget: Any, icon_name: str) -> None:
        super().__init__(widget)
        self.glyph = _VectorIconGlyph(icon_name, widget)
        widget.installEventFilter(self)
        self._layout_glyph(widget)

    def _arrow_rect(self, widget: Any) -> Any:
        option = QtWidgets.QStyleOptionComboBox()
        widget.initStyleOption(option)
        control = getattr(QtWidgets.QStyle, "CC_ComboBox", None)
        arrow = getattr(QtWidgets.QStyle, "SC_ComboBoxArrow", None)
        if control is None:
            control = QtWidgets.QStyle.ComplexControl.CC_ComboBox
            arrow = QtWidgets.QStyle.SubControl.SC_ComboBoxArrow
        return widget.style().subControlRect(
            control,
            option,
            arrow,
            widget,
        )

    def _layout_glyph(self, widget: Any) -> None:
        rect = self._arrow_rect(widget)
        if rect.isValid():
            self.glyph.setGeometry(rect)
            self.glyph.show()
            self.glyph.raise_()

    def eventFilter(self, watched: Any, event: Any) -> bool:
        glyph = getattr(self, "glyph", None)
        if glyph is not None:
            event_type = event.type()
            layout_events = tuple(
                _event_type(name)
                for name in ("Resize", "Show")
            )
            update_events = tuple(
                _event_type(name)
                for name in ("EnabledChange", "PaletteChange")
            )
            if event_type in layout_events:
                self._layout_glyph(watched)
            elif event_type in update_events:
                glyph.update()
        return super().eventFilter(watched, event)


def _install_combo_box_chevron(widget: Any, icon_name: str) -> Any:
    controller = _ComboBoxChevronController(widget, icon_name)
    widget._shadcn_qt_combo_chevron = controller
    return controller


__all__ = [
    "_install_combo_box_chevron",
    "_paint_vector_icon",
    "_vector_icon_path",
    "_ComboBoxChevronController",
    "_VectorIconButton",
    "_VectorIconGlyph",
]
