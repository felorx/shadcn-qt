"""Shared Chrome-style behavior for custom and adopted tab panes."""

from __future__ import annotations

from typing import Any

from shadcn_qt import _qt
from shadcn_qt.widgets._style import enable_antialiasing, semantic_color

QtCore, QtGui, QtWidgets = _qt.qt_modules()


def _qt_enum(name: str, group: str) -> Any:
    value = getattr(QtCore.Qt, name, None)
    if value is not None:
        return value
    return getattr(getattr(QtCore.Qt, group), name)


def _button_position(name: str) -> Any:
    value = getattr(QtWidgets.QTabBar, name, None)
    if value is not None:
        return value
    return getattr(QtWidgets.QTabBar.ButtonPosition, name)


def _mix_semantic_color(
    widget: Any,
    foreground_name: str,
    background_name: str,
    opacity: float,
) -> Any:
    foreground = semantic_color(widget, foreground_name)
    background = semantic_color(widget, background_name)
    channels = [
        round(
            foreground_component * opacity
            + background_component * (1.0 - opacity)
        )
        for foreground_component, background_component in zip(
            foreground.getRgb()[:3],
            background.getRgb()[:3],
        )
    ]
    return QtGui.QColor(*channels)


def _tab_body_rect(bar: Any, index: int) -> Any:
    rect = QtCore.QRectF(bar.tabRect(index)).adjusted(1.5, 0, -1.5, 0)
    if index == 0:
        rect.setLeft(rect.left() + 10.0)
    return rect


def _active_tab_paths(body_rect: Any, bar_rect: Any) -> tuple[Any, Any]:
    """Return Chrome's connected fill and its bottomless visible outline."""

    shoulder = 10.0
    top = body_rect.top() + 2.0
    bottom = bar_rect.bottom() + 1.0
    left = max(body_rect.left(), bar_rect.left() + shoulder + 0.5)
    right = min(body_rect.right(), bar_rect.right() - shoulder - 0.5)
    top_radius = 8.0

    outline = QtGui.QPainterPath()
    outline.moveTo(left - shoulder, bottom)
    outline.cubicTo(
        left - shoulder * 0.45,
        bottom,
        left,
        bottom - shoulder * 0.45,
        left,
        bottom - shoulder,
    )
    outline.lineTo(left, top + top_radius)
    outline.quadTo(left, top, left + top_radius, top)
    outline.lineTo(right - top_radius, top)
    outline.quadTo(right, top, right, top + top_radius)
    outline.lineTo(right, bottom - shoulder)
    outline.cubicTo(
        right,
        bottom - shoulder * 0.45,
        right + shoulder * 0.45,
        bottom,
        right + shoulder,
        bottom,
    )
    fill = QtGui.QPainterPath(outline)
    fill.lineTo(left - shoulder, bottom)
    fill.closeSubpath()
    return fill, outline


class TabPaneCloseButton(QtWidgets.QAbstractButton):
    """Small vector close button that is stable across Qt platform styles."""

    def __init__(self, bar: Any) -> None:
        super().__init__(bar)
        self.setObjectName("shadcnQtTabPaneCloseButton")
        self.setProperty("shadcn_qt_native_styling", False)
        self.setProperty("tabPaneCloseButton", True)
        self.setAccessibleName("Close tab")
        self.setFixedSize(24, 20)
        self.setMouseTracking(True)
        self.clicked.connect(self._request_close)

    def _request_close(self, checked: bool = False) -> None:
        del checked
        bar = self.parentWidget()
        if not isinstance(bar, QtWidgets.QTabBar):
            return
        position = self.mapTo(bar, self.rect().center())
        index = bar.tabAt(position)
        if index >= 0:
            bar.tabCloseRequested.emit(index)

    def paintEvent(self, event: Any) -> None:
        del event
        painter = QtGui.QPainter(self)
        enable_antialiasing(painter)
        side = 18.0
        rect = QtCore.QRectF(
            (self.width() - side) / 2.0,
            (self.height() - side) / 2.0,
            side,
            side,
        ).adjusted(1, 1, -1, -1)
        if self.underMouse():
            painter.setPen(_qt_enum("NoPen", "PenStyle"))
            painter.setBrush(semantic_color(self, "accent"))
            painter.drawEllipse(rect)

        foreground = semantic_color(self, "mutedForeground")
        if self.underMouse():
            foreground = semantic_color(self, "foreground")
        pen = QtGui.QPen(foreground, 1.5)
        pen.setCapStyle(_qt_enum("RoundCap", "PenCapStyle"))
        painter.setPen(pen)
        center = rect.center()
        offset = 3.0
        painter.drawLine(
            QtCore.QPointF(center.x() - offset, center.y() - offset),
            QtCore.QPointF(center.x() + offset, center.y() + offset),
        )
        painter.drawLine(
            QtCore.QPointF(center.x() + offset, center.y() - offset),
            QtCore.QPointF(center.x() - offset, center.y() + offset),
        )


def paint_tab_bar(bar: Any) -> None:
    """Paint a Chrome-like strip without platform-specific tab chrome."""

    painter = QtGui.QPainter(bar)
    enable_antialiasing(painter)
    border = semantic_color(bar, "border")
    input_border = semantic_color(bar, "input")
    foreground = semantic_color(bar, "foreground")
    muted_foreground = semantic_color(bar, "mutedForeground")
    page_surface = _mix_semantic_color(bar, "muted", "background", 0.50)
    accent = semantic_color(bar, "accent")
    ring = semantic_color(bar, "ring")

    cursor_position = bar.mapFromGlobal(QtGui.QCursor.pos())
    hovered_index = bar.tabAt(cursor_position) if bar.underMouse() else -1
    align_center = _qt_enum("AlignCenter", "AlignmentFlag")
    align_vcenter = _qt_enum("AlignVCenter", "AlignmentFlag")
    align_left = _qt_enum("AlignLeft", "AlignmentFlag")
    selected_index = bar.currentIndex()
    hovered_inactive_index = (
        hovered_index if hovered_index != selected_index else -1
    )
    for index in range(bar.count()):
        tab_rect = _tab_body_rect(bar, index).adjusted(0, 3.0, 0, -4.0)
        selected = index == bar.currentIndex()
        hovered = index == hovered_inactive_index
        if (
            not selected
            and not hovered
            and index < bar.count() - 1
            and index + 1 != selected_index
        ):
            painter.setPen(QtGui.QPen(border, 1))
            x = tab_rect.right() + 1
            painter.drawLine(
                QtCore.QPointF(x, tab_rect.top() + 7),
                QtCore.QPointF(x, tab_rect.bottom() - 7),
            )

    if hovered_inactive_index >= 0:
        hover_path, hover_outline = _active_tab_paths(
            _tab_body_rect(bar, hovered_inactive_index),
            QtCore.QRectF(bar.rect()),
        )
        painter.setPen(_qt_enum("NoPen", "PenStyle"))
        painter.setBrush(accent)
        painter.drawPath(hover_path)
        painter.setPen(QtGui.QPen(input_border, 1))
        painter.setBrush(_qt_enum("NoBrush", "BrushStyle"))
        painter.drawPath(hover_outline)

    if selected_index >= 0:
        selected_rect = _tab_body_rect(bar, selected_index)
        active_path, active_outline = _active_tab_paths(
            selected_rect,
            QtCore.QRectF(bar.rect()),
        )
        painter.setPen(_qt_enum("NoPen", "PenStyle"))
        painter.setBrush(page_surface)
        painter.drawPath(active_path)
        active_outline_color = ring if bar.hasFocus() else input_border
        painter.setPen(QtGui.QPen(active_outline_color, 1))
        painter.setBrush(_qt_enum("NoBrush", "BrushStyle"))
        painter.drawPath(active_outline)

    for index in range(bar.count()):
        tab_rect = _tab_body_rect(bar, index).adjusted(0, 2.0, 0, 0)
        selected = index == selected_index
        hovered = index == hovered_inactive_index
        enabled = bar.isTabEnabled(index)
        text_color = foreground if selected or hovered else muted_foreground
        if not enabled:
            text_color.setAlpha(128)
        painter.setPen(text_color)
        text_rect = tab_rect.adjusted(12, 0, -12, 0)
        right_button = bar.tabButton(index, _button_position("RightSide"))
        if right_button is not None:
            button_left = right_button.geometry().left()
            text_rect.setRight(min(text_rect.right(), button_left - 6.0))
        icon = bar.tabIcon(index)
        alignment = align_center
        if not icon.isNull():
            icon_size = 16
            icon_rect = QtCore.QRect(
                round(text_rect.left()),
                round(text_rect.center().y() - icon_size / 2),
                icon_size,
                icon_size,
            )
            icon.paint(painter, icon_rect)
            text_rect.adjust(icon_size + 8, 0, 0, 0)
            alignment = align_vcenter | align_left
        text = bar.fontMetrics().elidedText(
            bar.tabText(index),
            _qt_enum("ElideRight", "TextElideMode"),
            max(0, round(text_rect.width())),
        )
        painter.drawText(text_rect, int(alignment), text)


class TabPaneBar(QtWidgets.QTabBar):
    """QTabBar with deterministic Chrome-style painting."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self.setProperty("shadcn_qt_native_styling", False)
        self.setMouseTracking(True)

    def paintEvent(self, event: Any) -> None:
        del event
        paint_tab_bar(self)


def prepare_tab_pane(tab_widget: Any) -> None:
    """Suppress platform tab-strip details so shared painting stays authoritative."""

    bar = tab_widget.tabBar()
    bar.setDrawBase(False)
    styled_background = getattr(QtCore.Qt, "WA_StyledBackground", None)
    if styled_background is None:
        styled_background = QtCore.Qt.WidgetAttribute.WA_StyledBackground
    bar.setAttribute(styled_background, True)
    mac_focus_rect = getattr(QtCore.Qt, "WA_MacShowFocusRect", None)
    if mac_focus_rect is None:
        mac_focus_rect = getattr(
            QtCore.Qt.WidgetAttribute,
            "WA_MacShowFocusRect",
            None,
        )
    if mac_focus_rect is not None:
        # The shared painter renders keyboard focus on the outer connected-tab
        # silhouette.  Prevent the platform style from adding a second focus
        # rectangle around the title when focus moves between tabs.
        bar.setAttribute(mac_focus_rect, False)
    bar.setMouseTracking(True)
    bar.setElideMode(_qt_enum("ElideRight", "TextElideMode"))
    bar.setUsesScrollButtons(True)


def sync_tab_close_buttons(tab_widget: Any) -> None:
    """Replace platform close glyphs with stable vector buttons."""

    if not tab_widget.tabsClosable():
        return
    bar = tab_widget.tabBar()
    right = _button_position("RightSide")
    left = _button_position("LeftSide")
    for index in range(tab_widget.count()):
        replacement = None
        available_positions = []
        for position in (right, left):
            existing = bar.tabButton(index, position)
            if existing is None:
                available_positions.append(position)
                continue
            if isinstance(existing, TabPaneCloseButton) and position == right:
                replacement = existing
                continue
            if existing.metaObject().className() in {
                "CloseButton",
                "QTabBarCloseButton",
            }:
                bar.setTabButton(index, position, None)
                existing.deleteLater()
                available_positions.append(position)
        if replacement is None and right in available_positions:
            replacement = TabPaneCloseButton(bar)
            bar.setTabButton(index, right, replacement)
            replacement.show()


__all__ = [
    "TabPaneBar",
    "TabPaneCloseButton",
    "paint_tab_bar",
    "prepare_tab_pane",
    "sync_tab_close_buttons",
]
