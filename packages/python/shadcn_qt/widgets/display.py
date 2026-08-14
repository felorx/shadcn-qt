"""Data-display, feedback, and conversation components."""

from __future__ import annotations

from typing import Any, Iterable, Optional, Sequence, Union

from shadcn_qt import _qt
from shadcn_qt.widgets._helpers import initialize_component, refresh_style
from shadcn_qt.widgets._style import (
    enable_antialiasing,
    semantic_color,
    with_alpha,
)
from shadcn_qt.widgets.button import Button
from shadcn_qt.widgets.controls import Label

QtCore, QtGui, QtWidgets = _qt.qt_modules()


def _align_center() -> Any:
    value = getattr(QtCore.Qt, "AlignCenter", None)
    return value if value is not None else QtCore.Qt.AlignmentFlag.AlignCenter


def _align_vcenter() -> Any:
    value = getattr(QtCore.Qt, "AlignVCenter", None)
    return value if value is not None else QtCore.Qt.AlignmentFlag.AlignVCenter


class Avatar(QtWidgets.QLabel):
    def __init__(
        self,
        fallback: Union[str, Any] = "?",
        parent: Optional[Any] = None,
        *,
        size: int = 40,
    ) -> None:
        if isinstance(fallback, QtWidgets.QWidget) and parent is None:
            parent, fallback = fallback, "?"
        super().__init__(str(fallback), parent)
        initialize_component(self, "avatar")
        self._fallback = str(fallback)
        self._avatar_size = 40
        self.setAlignment(_align_center())
        self.setScaledContents(False)
        self.set_avatar_size(size)

    def get_fallback(self) -> str:
        return self._fallback

    def set_fallback(self, fallback: str) -> None:
        self._fallback = fallback
        if self.pixmap() is None or self.pixmap().isNull():
            self.setText(fallback)

    def avatar_size(self) -> int:
        return self._avatar_size

    def set_avatar_size(self, size: int) -> None:
        self._avatar_size = max(16, int(size))
        self.setFixedSize(self._avatar_size, self._avatar_size)
        refresh_style(self)

    def setImage(self, source: Union[str, Any]) -> bool:
        pixmap = (
            source if isinstance(source, QtGui.QPixmap) else QtGui.QPixmap(str(source))
        )
        if pixmap.isNull():
            self.clear()
            self.setText(self._fallback)
            return False
        self.setPixmap(pixmap)
        self.update()
        return True

    def paintEvent(self, event: Any) -> None:
        del event
        painter = QtGui.QPainter(self)
        enable_antialiasing(painter)
        bounds = QtCore.QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        muted = semantic_color(self, "muted", fallback_role="Button")
        border = semantic_color(self, "border", fallback_role="Mid")
        painter.setPen(QtGui.QPen(border, 1))
        painter.setBrush(muted)
        painter.drawEllipse(bounds)
        pixmap = self.pixmap()
        if pixmap is not None and not pixmap.isNull():
            painter.save()
            path = QtGui.QPainterPath()
            path.addEllipse(bounds.adjusted(1, 1, -1, -1))
            painter.setClipPath(path)
            aspect = getattr(QtCore.Qt, "KeepAspectRatioByExpanding", None)
            smooth = getattr(QtCore.Qt, "SmoothTransformation", None)
            if aspect is None:
                aspect = QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding
                smooth = QtCore.Qt.TransformationMode.SmoothTransformation
            scaled = pixmap.scaled(self.size(), aspect, smooth)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.restore()
        else:
            painter.setPen(semantic_color(self, "mutedForeground"))
            painter.drawText(self.rect(), int(_align_center()), self._fallback)

    getFallback = get_fallback
    setFallback = set_fallback
    getAvatarSize = avatar_size
    setAvatarSize = set_avatar_size
    fallback = _qt.qt_property(str, fget=get_fallback, fset=set_fallback)
    avatarSize = _qt.qt_property(int, fget=avatar_size, fset=set_avatar_size)


class Skeleton(QtWidgets.QFrame):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "skeleton")
        self.setMinimumHeight(16)
        effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self._pulse = QtCore.QVariantAnimation(self)
        self._pulse.setDuration(1400)
        self._pulse.setLoopCount(-1)
        self._pulse.setKeyValueAt(0.0, 0.55)
        self._pulse.setKeyValueAt(0.5, 1.0)
        self._pulse.setKeyValueAt(1.0, 0.55)
        self._pulse.valueChanged.connect(lambda value: effect.setOpacity(float(value)))
        self._pulse.start()


class Spinner(QtWidgets.QProgressBar):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "spinner")
        self.setRange(0, 0)
        self.setTextVisible(False)
        self.setFixedSize(16, 16)
        self._angle = 0
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._advance)
        self._timer.start()

    def _advance(self) -> None:
        self._angle = (self._angle - 18) % 360
        self.update()

    def paintEvent(self, event: Any) -> None:
        del event
        painter = QtGui.QPainter(self)
        enable_antialiasing(painter)
        color = semantic_color(self, "primary", fallback_role="Highlight")
        painter.setPen(QtGui.QPen(with_alpha(color, 56), 2))
        bounds = QtCore.QRectF(self.rect()).adjusted(2, 2, -2, -2)
        painter.drawEllipse(bounds)
        pen = QtGui.QPen(color, 2)
        cap = getattr(QtCore.Qt, "RoundCap", None)
        if cap is None:
            cap = QtCore.Qt.PenCapStyle.RoundCap
        pen.setCapStyle(cap)
        painter.setPen(pen)
        painter.drawArc(bounds, self._angle * 16, 100 * 16)


class Kbd(QtWidgets.QLabel):
    def __init__(
        self, text: Union[str, Any] = "⌘K", parent: Optional[Any] = None
    ) -> None:
        if isinstance(text, QtWidgets.QWidget) and parent is None:
            parent, text = text, "⌘K"
        super().__init__(str(text), parent)
        initialize_component(self, "kbd")
        self.setAlignment(_align_center())


class Empty(QtWidgets.QFrame):
    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        title: str = "No results",
        description: str = "There is nothing here yet.",
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "empty")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)
        layout.setAlignment(_align_center())
        self.titleLabel = Label(title, self, variant="large")
        self.descriptionLabel = Label(description, self, variant="muted")
        self.actionContainer = QtWidgets.QWidget(self)
        self.actionLayout = QtWidgets.QHBoxLayout(self.actionContainer)
        self.actionLayout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        layout.addWidget(self.titleLabel, 0, _align_center())
        layout.addWidget(self.descriptionLabel, 0, _align_center())
        layout.addWidget(self.actionContainer, 0, _align_center())
        layout.addStretch(1)

    def setAction(self, widget: Any) -> None:
        self.actionLayout.addWidget(widget)

    def get_title(self) -> str:
        return self.titleLabel.text()

    def set_title(self, value: str) -> None:
        self.titleLabel.setText(value)

    def get_description(self) -> str:
        return self.descriptionLabel.text()

    def set_description(self, value: str) -> None:
        self.descriptionLabel.setText(value)

    getTitle = get_title
    setTitle = set_title
    getDescription = get_description
    setDescription = set_description
    title = _qt.qt_property(str, fget=get_title, fset=set_title)
    description = _qt.qt_property(str, fget=get_description, fset=set_description)


class _ItemActionButton(Button):
    def __init__(self, parent: Any) -> None:
        super().__init__("", parent, variant="ghost", size="icon")
        self.setAccessibleName("Open item")

    def sizeHint(self) -> Any:
        return QtCore.QSize(36, 36)

    def minimumSizeHint(self) -> Any:
        return QtCore.QSize(36, 36)

    def _icon_path(self) -> Any:
        center = QtCore.QRectF(self.rect()).center()
        path = QtGui.QPainterPath()
        path.moveTo(center.x() - 2.0, center.y() - 4.0)
        path.lineTo(center.x() + 2.0, center.y())
        path.lineTo(center.x() - 2.0, center.y() + 4.0)
        return path

    def paintEvent(self, event: Any) -> None:
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        enable_antialiasing(painter)
        color = semantic_color(self, "foreground")
        if not self.isEnabled():
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
        painter.drawPath(self._icon_path())


class Item(QtWidgets.QFrame):
    triggered = _qt.qt_signal()

    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        title: str = "Item",
        description: str = "",
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "item")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        self.media = Label("", self)
        self.content = QtWidgets.QWidget(self)
        self.content.setObjectName("shadcnQtItemContent")
        self.content.setAutoFillBackground(False)
        content_layout = QtWidgets.QVBoxLayout(self.content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)
        self.titleLabel = Label(title, self, variant="small")
        self.descriptionLabel = Label(description, self, variant="muted")
        content_layout.addWidget(self.titleLabel)
        content_layout.addWidget(self.descriptionLabel)
        self.actionContainer = QtWidgets.QWidget(self)
        self.actionContainer.setObjectName("shadcnQtItemAction")
        self.actionContainer.setFixedSize(36, 36)
        self.actionContainer.setAutoFillBackground(False)
        action_layout = QtWidgets.QHBoxLayout(self.actionContainer)
        action_layout.setContentsMargins(0, 0, 0, 0)
        self.action = _ItemActionButton(self.actionContainer)
        action_layout.addWidget(self.action)
        self.action.clicked.connect(self.triggered)
        layout.addWidget(self.media)
        layout.addWidget(self.content, 1)
        layout.addWidget(self.actionContainer, 0, _align_vcenter())

    def get_title(self) -> str:
        return self.titleLabel.text()

    def set_title(self, title: str) -> None:
        self.titleLabel.setText(title)

    def get_description(self) -> str:
        return self.descriptionLabel.text()

    def set_description(self, description: str) -> None:
        self.descriptionLabel.setText(description)
        self.descriptionLabel.setVisible(bool(description))

    getTitle = get_title
    setTitle = set_title
    getDescription = get_description
    setDescription = set_description
    title = _qt.qt_property(str, fget=get_title, fset=set_title)
    description = _qt.qt_property(str, fget=get_description, fset=set_description)


class Table(QtWidgets.QTableWidget):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "table")
        self.setAlternatingRowColors(False)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(40)
        self.horizontalHeader().setFixedHeight(40)


class DataTable(QtWidgets.QTableView):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "data-table")
        self._source_model = QtGui.QStandardItemModel(self)
        self._proxy_model = QtCore.QSortFilterProxyModel(self)
        self._proxy_model.setSourceModel(self._source_model)
        self.setModel(self._proxy_model)
        self.setSortingEnabled(True)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(40)
        self.horizontalHeader().setFixedHeight(40)

    def setRows(self, headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> None:
        self._source_model.clear()
        self._source_model.setHorizontalHeaderLabels(list(headers))
        for row in rows:
            self._source_model.appendRow(
                [QtGui.QStandardItem(str(value)) for value in row]
            )
        self.resizeColumnsToContents()

    def setFilterText(self, text: str) -> None:
        self._proxy_model.setFilterFixedString(text)


def _style_state(name: str) -> Any:
    value = getattr(QtWidgets.QStyle, name, None)
    if value is not None:
        return value
    return getattr(QtWidgets.QStyle.StateFlag, name)


class _CalendarDelegate(QtWidgets.QStyledItemDelegate):
    """Paint QCalendarWidget cells with new-york day-button geometry."""

    def paint(self, painter: Any, option: Any, index: Any) -> None:
        painter.save()
        enable_antialiasing(painter)
        view = self.parent()
        foreground = semantic_color(view, "foreground", fallback_role="WindowText")
        muted = semantic_color(view, "muted", fallback_role="AlternateBase")
        muted_foreground = semantic_color(view, "mutedForeground")
        primary = semantic_color(view, "primary", fallback_role="Highlight")
        primary_foreground = semantic_color(
            view, "primaryForeground", fallback_role="HighlightedText"
        )
        accent = semantic_color(view, "accent", fallback_role="AlternateBase")
        text = str(index.data() or "")
        rect = QtCore.QRectF(option.rect)
        if index.row() == 0:
            painter.setPen(_qt_pen_none())
            painter.setBrush(muted)
            painter.drawRect(rect)
            painter.setPen(muted_foreground)
            painter.drawText(rect, int(_align_center()), text)
            painter.restore()
            return

        side = min(32.0, rect.height() - 4.0)
        day_rect = QtCore.QRectF(
            rect.center().x() - side / 2,
            rect.center().y() - side / 2,
            side,
            side,
        )
        selected = bool(option.state & _style_state("State_Selected")) or (
            view.currentIndex() == index
        )
        hovered = bool(option.state & _style_state("State_MouseOver"))
        enabled = bool(option.state & _style_state("State_Enabled"))
        if selected:
            painter.setPen(_qt_pen_none())
            painter.setBrush(primary)
            painter.drawRoundedRect(day_rect, 6, 6)
            painter.setPen(primary_foreground)
        elif hovered:
            painter.setPen(_qt_pen_none())
            painter.setBrush(accent)
            painter.drawRoundedRect(day_rect, 6, 6)
            painter.setPen(foreground)
        else:
            painter.setPen(foreground if enabled else muted_foreground)
        painter.drawText(day_rect, int(_align_center()), text)
        painter.restore()


def _qt_pen_none() -> Any:
    value = getattr(QtCore.Qt, "NoPen", None)
    if value is not None:
        return value
    return QtCore.Qt.PenStyle.NoPen


class _CalendarMonthIndicator(QtWidgets.QWidget):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent)
        transparent = getattr(QtCore.Qt, "WA_TransparentForMouseEvents", None)
        if transparent is None:
            transparent = QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents
        self.setAttribute(transparent, True)

    def _icon_path(self) -> Any:
        center = QtCore.QRectF(self.rect()).center()
        path = QtGui.QPainterPath()
        path.moveTo(center.x() - 4.0, center.y() - 2.0)
        path.lineTo(center.x(), center.y() + 2.0)
        path.lineTo(center.x() + 4.0, center.y() - 2.0)
        return path

    def paintEvent(self, event: Any) -> None:
        del event
        painter = QtGui.QPainter(self)
        enable_antialiasing(painter)
        pen = QtGui.QPen(semantic_color(self, "mutedForeground"), 1.5)
        cap = getattr(QtCore.Qt, "RoundCap", None)
        join = getattr(QtCore.Qt, "RoundJoin", None)
        if cap is None:
            cap = QtCore.Qt.PenCapStyle.RoundCap
            join = QtCore.Qt.PenJoinStyle.RoundJoin
        pen.setCapStyle(cap)
        pen.setJoinStyle(join)
        painter.setPen(pen)
        painter.drawPath(self._icon_path())


class Calendar(QtWidgets.QCalendarWidget):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "calendar")
        self.setGridVisible(False)
        no_vertical_header = getattr(
            QtWidgets.QCalendarWidget, "NoVerticalHeader", None
        )
        if no_vertical_header is None:
            no_vertical_header = (
                QtWidgets.QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
            )
        self.setVerticalHeaderFormat(no_vertical_header)
        for object_name, glyph in (
            ("qt_calendar_prevmonth", "‹"),
            ("qt_calendar_nextmonth", "›"),
        ):
            button = self.findChild(QtWidgets.QToolButton, object_name)
            if button is not None:
                button.setIcon(QtGui.QIcon())
                button.setText(glyph)
                button.setFixedSize(32, 32)
        self._month_button = self.findChild(
            QtWidgets.QToolButton, "qt_calendar_monthbutton"
        )
        self._month_indicator = None
        if self._month_button is not None:
            self._month_button.setIcon(QtGui.QIcon())
            self._month_button.installEventFilter(self)
            self._month_indicator = _CalendarMonthIndicator(self._month_button)
            self._layout_month_indicator()
        self._sync_text_formats()
        self._install_delegate()
        self.currentPageChanged.connect(
            lambda *_: QtCore.QTimer.singleShot(0, self._install_delegate)
        )

    def _install_delegate(self) -> None:
        calendar_view = self.findChild(
            QtWidgets.QTableView, "qt_calendar_calendarview"
        )
        if calendar_view is not None:
            if getattr(self, "_calendar_view", None) is not calendar_view:
                calendar_view.installEventFilter(self)
                self._calendar_view = calendar_view
            calendar_view.setMouseTracking(True)
            calendar_view.verticalHeader().setMinimumSectionSize(36)
            calendar_view.verticalHeader().setDefaultSectionSize(36)
            calendar_view.setItemDelegate(_CalendarDelegate(calendar_view))

    def _layout_month_indicator(self) -> None:
        if self._month_button is None or self._month_indicator is None:
            return
        self._month_indicator.setGeometry(
            max(0, self._month_button.width() - 20),
            0,
            16,
            self._month_button.height(),
        )
        self._month_indicator.show()
        self._month_indicator.raise_()

    def eventFilter(self, watched: Any, event: Any) -> bool:
        if watched is getattr(self, "_month_button", None):
            resize = getattr(QtCore.QEvent, "Resize", None)
            show = getattr(QtCore.QEvent, "Show", None)
            if resize is None:
                resize = QtCore.QEvent.Type.Resize
                show = QtCore.QEvent.Type.Show
            if event.type() in (resize, show):
                self._layout_month_indicator()
        calendar_view = getattr(self, "_calendar_view", None)
        if watched is calendar_view:
            paint = getattr(QtCore.QEvent, "Paint", None)
            if paint is None:
                paint = QtCore.QEvent.Type.Paint
            if event.type() == paint and not isinstance(
                calendar_view.itemDelegate(), _CalendarDelegate
            ):
                calendar_view.setItemDelegate(_CalendarDelegate(calendar_view))
        return super().eventFilter(watched, event)

    def _sync_text_formats(self) -> None:
        foreground = semantic_color(self, "foreground", fallback_role="WindowText")
        text_format = QtGui.QTextCharFormat()
        text_format.setForeground(foreground)
        days = (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        )
        day_scope = getattr(QtCore.Qt, "DayOfWeek", None)
        for name in days:
            day = getattr(QtCore.Qt, name, None)
            if day is None:
                day = getattr(day_scope, name)
            self.setWeekdayTextFormat(day, text_format)
        self.setHeaderTextFormat(text_format)

    def changeEvent(self, event: Any) -> None:
        palette_change = getattr(QtCore.QEvent, "PaletteChange", None)
        if palette_change is None:
            palette_change = QtCore.QEvent.Type.PaletteChange
        if event.type() == palette_change:
            self._sync_text_formats()
            month_indicator = getattr(self, "_month_indicator", None)
            if month_indicator is not None:
                month_indicator.update()
            self._install_delegate()
        super().changeEvent(event)

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        QtCore.QTimer.singleShot(0, self._install_delegate)


class Chart(QtWidgets.QFrame):
    """A lightweight, dependency-free line or bar chart."""

    TYPES = ("line", "bar")

    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        chart_type: str = "line",
        values: Union[str, Iterable[float]] = "12, 28, 18, 42, 34",
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "chart")
        self._chart_type = "line"
        self._values = []
        self.setMinimumSize(160, 100)
        self.set_chart_type(chart_type)
        self.set_values(values)

    def get_chart_type(self) -> str:
        return self._chart_type

    def set_chart_type(self, chart_type: str) -> None:
        if chart_type not in self.TYPES:
            raise ValueError(f"chart_type must be one of {self.TYPES}")
        self._chart_type = chart_type
        self.update()
        refresh_style(self)

    def get_values(self) -> str:
        return ", ".join(f"{value:g}" for value in self._values)

    def set_values(self, values: Union[str, Iterable[float]]) -> None:
        parts = values.split(",") if isinstance(values, str) else values
        self._values = [
            float(value.strip() if isinstance(value, str) else value) for value in parts
        ]
        self.update()

    def valuesList(self) -> list[float]:
        return list(self._values)

    def paintEvent(self, event: Any) -> None:
        super().paintEvent(event)
        if not self._values:
            return
        painter = QtGui.QPainter(self)
        antialias = getattr(QtGui.QPainter, "Antialiasing", None)
        if antialias is None:
            antialias = QtGui.QPainter.RenderHint.Antialiasing
        painter.setRenderHint(antialias, True)
        bounds = self.rect().adjusted(12, 12, -12, -12)
        low, high = min(self._values), max(self._values)
        span = high - low or 1.0
        color = self.palette().highlight().color()
        if self._chart_type == "bar":
            no_pen = getattr(QtCore.Qt, "NoPen", None)
            if no_pen is None:
                no_pen = QtCore.Qt.PenStyle.NoPen
            painter.setPen(no_pen)
            painter.setBrush(color)
            cell_width = bounds.width() / max(1, len(self._values))
            for index, value in enumerate(self._values):
                height = max(2.0, (value - low) / span * bounds.height())
                painter.drawRect(
                    QtCore.QRectF(
                        bounds.left() + index * cell_width + cell_width * 0.15,
                        bounds.bottom() - height,
                        cell_width * 0.7,
                        height,
                    )
                )
        else:
            painter.setPen(QtGui.QPen(color, 2))
            step = bounds.width() / max(1, len(self._values) - 1)
            points = [
                QtCore.QPointF(
                    bounds.left() + index * step,
                    bounds.bottom() - (value - low) / span * bounds.height(),
                )
                for index, value in enumerate(self._values)
            ]
            for start, end in zip(points, points[1:]):
                painter.drawLine(start, end)

    getChartType = get_chart_type
    setChartType = set_chart_type
    getValues = get_values
    setValues = set_values
    chartType = _qt.qt_property(str, fget=get_chart_type, fset=set_chart_type)
    values = _qt.qt_property(str, fget=get_values, fset=set_values)


class Typography(QtWidgets.QLabel):
    """shadcn typography presets exposed as a Designer-editable Qt widget."""

    LEVELS = (
        "h1",
        "h2",
        "h3",
        "h4",
        "p",
        "blockquote",
        "code",
        "lead",
        "large",
        "small",
        "muted",
    )

    def __init__(
        self,
        text: Union[str, Any] = "Typography",
        parent: Optional[Any] = None,
        *,
        level: str = "p",
    ) -> None:
        if isinstance(text, QtWidgets.QWidget) and parent is None:
            parent, text = text, "Typography"
        super().__init__(str(text), parent)
        initialize_component(self, "typography")
        self._level = "p"
        self.setWordWrap(True)
        self.set_level(level)

    def get_level(self) -> str:
        return self._level

    def set_level(self, level: str) -> None:
        if level not in self.LEVELS:
            raise ValueError(f"level must be one of {self.LEVELS}")
        self._level = level
        refresh_style(self)

    getLevel = get_level
    setLevel = set_level
    level = _qt.qt_property(str, fget=get_level, fset=set_level)


class Attachment(QtWidgets.QFrame):
    removed = _qt.qt_signal()

    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        name: str = "attachment",
        detail: str = "",
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "attachment")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        self.nameLabel = Label(name, self, variant="small")
        self.detailLabel = Label(detail, self, variant="muted")
        self.removeButton = Button("×", self, variant="ghost", size="icon")
        self.removeButton.clicked.connect(self.removed)
        layout.addWidget(self.nameLabel)
        layout.addWidget(self.detailLabel, 1)
        layout.addWidget(self.removeButton)


class Marker(QtWidgets.QLabel):
    VARIANTS = ("default", "status", "separator")

    def __init__(
        self,
        text: Union[str, Any] = "Status",
        parent: Optional[Any] = None,
        *,
        variant: str = "default",
    ) -> None:
        if isinstance(text, QtWidgets.QWidget) and parent is None:
            parent, text = text, "Status"
        super().__init__(str(text), parent)
        initialize_component(self, "marker")
        self._variant = "default"
        self.set_variant(variant)

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, variant: str) -> None:
        if variant not in self.VARIANTS:
            raise ValueError(f"variant must be one of {self.VARIANTS}")
        self._variant = variant
        refresh_style(self)

    getVariant = get_variant
    setVariant = set_variant
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)


class Bubble(QtWidgets.QFrame):
    VARIANTS = ("default", "secondary", "outline")
    ALIGNMENTS = ("start", "end")

    def __init__(
        self,
        text: Union[str, Any] = "Message",
        parent: Optional[Any] = None,
        *,
        variant: str = "default",
        alignment: str = "start",
    ) -> None:
        if isinstance(text, QtWidgets.QWidget) and parent is None:
            parent, text = text, "Message"
        super().__init__(parent)
        initialize_component(self, "bubble")
        self._variant = "default"
        self._alignment = "start"
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        self.contentLabel = Label(str(text), self)
        self.contentLabel.setWordWrap(True)
        layout.addWidget(self.contentLabel)
        self.set_variant(variant)
        self.set_alignment(alignment)

    def text(self) -> str:
        return self.contentLabel.text()

    def setText(self, text: str) -> None:
        self.contentLabel.setText(text)

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, variant: str) -> None:
        if variant not in self.VARIANTS:
            raise ValueError(f"variant must be one of {self.VARIANTS}")
        self._variant = variant
        refresh_style(self)

    def get_alignment(self) -> str:
        return self._alignment

    def set_alignment(self, alignment: str) -> None:
        if alignment not in self.ALIGNMENTS:
            raise ValueError(f"alignment must be one of {self.ALIGNMENTS}")
        self._alignment = alignment
        refresh_style(self)

    getVariant = get_variant
    setVariant = set_variant
    getAlignment = get_alignment
    setAlignment = set_alignment
    getContent = text
    setContent = setText
    content = _qt.qt_property(str, fget=text, fset=setText)
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)
    alignment = _qt.qt_property(str, fget=get_alignment, fset=set_alignment)


class Message(QtWidgets.QFrame):
    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        author: str = "",
        content: str = "",
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "message")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)
        self.authorLabel = Label(author, self, variant="small")
        self.bubble = Bubble(content, self)
        layout.addWidget(self.authorLabel)
        layout.addWidget(self.bubble)

    def get_author(self) -> str:
        return self.authorLabel.text()

    def set_author(self, author: str) -> None:
        self.authorLabel.setText(author)

    def get_content(self) -> str:
        return self.bubble.text()

    def set_content(self, content: str) -> None:
        self.bubble.setText(content)

    getAuthor = get_author
    setAuthor = set_author
    getContent = get_content
    setContent = set_content
    author = _qt.qt_property(str, fget=get_author, fset=set_author)
    content = _qt.qt_property(str, fget=get_content, fset=set_content)


class MessageScroller(QtWidgets.QScrollArea):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "message-scroller")
        self.setWidgetResizable(True)
        self.viewportWidget = QtWidgets.QWidget(self)
        self.messageLayout = QtWidgets.QVBoxLayout(self.viewportWidget)
        self.messageLayout.setContentsMargins(8, 8, 8, 8)
        self.messageLayout.setSpacing(8)
        self.messageLayout.addStretch(1)
        self.setWidget(self.viewportWidget)

    def addMessage(self, message: Any) -> None:
        self.messageLayout.insertWidget(self.messageLayout.count() - 1, message)
        QtCore.QTimer.singleShot(0, self.scrollToBottom)

    def scrollToBottom(self) -> None:
        bar = self.verticalScrollBar()
        bar.setValue(bar.maximum())


__all__ = [
    "Attachment",
    "Avatar",
    "Bubble",
    "Calendar",
    "Chart",
    "DataTable",
    "Empty",
    "Item",
    "Kbd",
    "Marker",
    "Message",
    "MessageScroller",
    "Skeleton",
    "Spinner",
    "Table",
    "Typography",
]
