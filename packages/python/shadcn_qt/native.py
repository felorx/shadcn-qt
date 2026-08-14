"""Opt-in styling for existing native Qt widgets.

The adapter adds the same dynamic properties used by shadcn-qt subclasses to
compatible standard widgets.  It deliberately supplies only safe defaults;
semantic choices such as Card vs Alert or Checkbox vs Switch remain explicit.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Tuple

from shadcn_qt import _qt

_ADAPTER_ATTRIBUTE = "_shadcn_qt_native_widget_styling_adapter"
_ADOPTED_PROPERTY = "shadcn_qt_native_adopted"
_ADDED_PROPERTIES = "shadcn_qt_native_properties"
_PREFERENCE_PROPERTY = "shadcn_qt_native_styling"
_STYLE_PROPERTIES = frozenset(
    {
        "shadcn_qt_component",
        "variant",
        "shadcnSize",
        "invalid",
        "nativeKind",
    }
)
_ADAPTER_TYPE: Optional[Any] = None
_CALENDAR_DELEGATE_TYPE: Optional[Any] = None
_ENHANCEMENT_FILTER_TYPE: Optional[Any] = None
_NATIVE_GLYPH_TYPE: Optional[Any] = None


def _refresh_style(widget: Any) -> None:
    style = widget.style()
    if style is not None:
        style.unpolish(widget)
        style.polish(widget)
    widget.update()


def _is_internal_widget(widget: Any, widgets: Any) -> bool:
    # Embedded editors are styled by their owning complex control. Applying a
    # second Input frame would produce a visible double border. Other Qt-owned
    # children are deliberately adopted so compatibility mode has no native
    # visual gaps.
    if isinstance(widget, widgets.QLineEdit):
        parent = widget.parentWidget()
        if isinstance(parent, (widgets.QComboBox, widgets.QAbstractSpinBox)):
            return True
    return False


def _is_instance(widget: Any, widgets: Any, class_name: str) -> bool:
    widget_type = getattr(widgets, class_name, None)
    return widget_type is not None and isinstance(widget, widget_type)


def _dialog_kind(widget: Any, widgets: Any) -> str:
    for class_name, kind in (
        ("QMessageBox", "message-box"),
        ("QFileDialog", "file-dialog"),
        ("QColorDialog", "color-dialog"),
        ("QFontDialog", "font-dialog"),
        ("QInputDialog", "input-dialog"),
        ("QProgressDialog", "progress-dialog"),
        ("QErrorMessage", "error-message"),
        ("QWizard", "wizard"),
    ):
        if _is_instance(widget, widgets, class_name):
            return kind
    return "dialog"


def _button_variant(widget: Any, widgets: Any) -> str:
    parent = widget.parentWidget()
    if not isinstance(parent, widgets.QDialogButtonBox):
        return "default"
    role = parent.buttonRole(widget)
    role_name = getattr(role, "name", str(role)).split(".")[-1]
    if role_name == "DestructiveRole":
        return "destructive"
    if role_name in {"RejectRole", "NoRole", "ResetRole", "HelpRole"}:
        return "outline"
    if role_name in {"ApplyRole", "ActionRole"}:
        return "secondary"
    return "default"


def _frame_kind(widget: Any, widgets: Any) -> str:
    shape = widget.frameShape()
    shape_name = getattr(shape, "name", str(shape)).split(".")[-1]
    if shape_name in {"HLine", "VLine"}:
        return shape_name.casefold()
    if shape_name in {"Panel", "StyledPanel", "Box", "WinPanel"}:
        return "panel"
    return "plain"


def _native_defaults(widget: Any, widgets: Any) -> Optional[Dict[str, Any]]:
    """Return the default shadcn-qt properties for a native widget type."""

    if isinstance(widget, widgets.QPushButton):
        kind = (
            "command-link"
            if _is_instance(widget, widgets, "QCommandLinkButton")
            else "push-button"
        )
        return {
            "shadcn_qt_component": "button",
            "variant": _button_variant(widget, widgets),
            "shadcnSize": "default",
            "nativeKind": kind,
        }

    specs: Iterable[Tuple[Any, str, Dict[str, Any]]] = (
        (widgets.QLineEdit, "input", {"invalid": False, "nativeKind": "line-edit"}),
        (widgets.QPlainTextEdit, "textarea", {"invalid": False, "nativeKind": "plain-text-edit"}),
        (widgets.QTextEdit, "text-edit", {"invalid": False, "nativeKind": "text-edit"}),
        (widgets.QCheckBox, "checkbox", {"nativeKind": "check-box"}),
        (widgets.QRadioButton, "radio", {"nativeKind": "radio-button"}),
        (widgets.QToolButton, "tool-button", {"variant": "default", "nativeKind": "tool-button"}),
        (widgets.QKeySequenceEdit, "key-sequence-edit", {"invalid": False, "nativeKind": "key-sequence-edit"}),
        (widgets.QDateEdit, "date-picker", {"nativeKind": "date-edit"}),
        (widgets.QDateTimeEdit, "date-picker", {"nativeKind": "date-time-edit"}),
        (widgets.QAbstractSpinBox, "spin-box", {"invalid": False, "nativeKind": type(widget).__name__}),
        (widgets.QComboBox, "select", {"nativeKind": type(widget).__name__}),
        (widgets.QSlider, "slider", {"nativeKind": "slider"}),
        (widgets.QDial, "dial", {"nativeKind": "dial"}),
        (widgets.QScrollBar, "scrollbar", {"nativeKind": "scroll-bar"}),
        (widgets.QProgressBar, "progress", {"nativeKind": "progress-bar"}),
        (widgets.QTabWidget, "tabs", {"nativeKind": "tab-widget"}),
        (widgets.QTabBar, "tab-bar", {"nativeKind": "tab-bar"}),
        (widgets.QToolBox, "toolbox", {"nativeKind": "tool-box"}),
        (widgets.QStackedWidget, "stacked-widget", {"nativeKind": "stacked-widget"}),
        (widgets.QTableWidget, "table", {"nativeKind": "table-widget"}),
        (widgets.QTableView, "data-table", {"nativeKind": "table-view"}),
        (widgets.QTreeView, "tree-view", {"nativeKind": "tree-view"}),
        (widgets.QListView, "list-view", {"nativeKind": "list-view"}),
        (widgets.QColumnView, "column-view", {"nativeKind": "column-view"}),
        (widgets.QHeaderView, "header-view", {"nativeKind": "header-view"}),
        (widgets.QAbstractItemView, "item-view", {"nativeKind": type(widget).__name__}),
        (widgets.QCalendarWidget, "calendar", {"nativeKind": "calendar-widget"}),
        (widgets.QMdiArea, "mdi-area", {"nativeKind": "mdi-area"}),
        (widgets.QGraphicsView, "graphics-view", {"nativeKind": "graphics-view"}),
        (widgets.QScrollArea, "scroll-area", {"nativeKind": "scroll-area"}),
        (widgets.QAbstractScrollArea, "scroll-area", {"nativeKind": type(widget).__name__}),
        (widgets.QMenuBar, "menubar", {"nativeKind": "menu-bar"}),
        (widgets.QMenu, "menu", {"nativeKind": "menu"}),
        (widgets.QToolBar, "toolbar", {"nativeKind": "tool-bar"}),
        (widgets.QStatusBar, "statusbar", {"nativeKind": "status-bar"}),
        (widgets.QDockWidget, "dock-widget", {"nativeKind": "dock-widget"}),
        (widgets.QGroupBox, "group-box", {"nativeKind": "group-box"}),
        (widgets.QDialogButtonBox, "dialog-button-box", {"nativeKind": "dialog-button-box"}),
        (widgets.QSplitter, "resizable", {"nativeKind": "splitter"}),
        (widgets.QLCDNumber, "lcd-number", {"nativeKind": "lcd-number"}),
        (widgets.QLabel, "label", {"variant": "default", "nativeKind": "label"}),
        (widgets.QFocusFrame, "focus-frame", {"nativeKind": "focus-frame"}),
        (widgets.QFrame, "frame", {"nativeKind": "frame"}),
        (widgets.QMdiSubWindow, "mdi-subwindow", {"nativeKind": "mdi-subwindow"}),
        (widgets.QWizardPage, "wizard-page", {"nativeKind": "wizard-page"}),
        (widgets.QDialog, "native-dialog", {"nativeKind": _dialog_kind(widget, widgets)}),
        (widgets.QMainWindow, "main-window", {"nativeKind": "main-window"}),
        (widgets.QSizeGrip, "size-grip", {"nativeKind": "size-grip"}),
        (widgets.QRubberBand, "rubber-band", {"nativeKind": "rubber-band"}),
        (widgets.QAbstractButton, "button", {"variant": "default", "shadcnSize": "default", "nativeKind": type(widget).__name__}),
        (widgets.QAbstractSlider, "slider", {"nativeKind": type(widget).__name__}),
        (widgets.QWidget, "widget", {"nativeKind": type(widget).__name__}),
    )
    for widget_type, component, defaults in specs:
        if isinstance(widget, widget_type):
            if widget_type is widgets.QFrame:
                defaults = {**defaults, "nativeKind": _frame_kind(widget, widgets)}
                if defaults["nativeKind"] in {"hline", "vline"}:
                    component = "native-separator"
            return {"shadcn_qt_component": component, **defaults}
    return None


def _qt_enum(core: Any, name: str, group: str) -> Any:
    direct = getattr(core.Qt, name, None)
    if direct is not None:
        return direct
    return getattr(getattr(core.Qt, group), name)


def _palette_role(gui: Any, name: str) -> Any:
    direct = getattr(gui.QPalette, name, None)
    if direct is not None:
        return direct
    return getattr(gui.QPalette.ColorRole, name)


def _semantic_color(widget: Any, gui: Any, name: str, fallback: str) -> Any:
    _, _, widgets = _qt.qt_modules()
    app = widgets.QApplication.instance()
    value = app.property(f"shadcn_qt_color_{name}") if app is not None else None
    color = gui.QColor(str(value)) if value else gui.QColor()
    if color.isValid():
        return color
    return widget.palette().color(_palette_role(gui, fallback))


def _with_alpha(gui: Any, color: Any, alpha: int) -> Any:
    result = gui.QColor(color)
    result.setAlpha(max(0, min(255, int(alpha))))
    return result


def _paint_native_choice(widget: Any, core: Any, gui: Any, widgets: Any) -> bool:
    component = widget.property("shadcn_qt_component")
    if component not in {"checkbox", "radio"}:
        return False

    painter = gui.QPainter(widget)
    antialiasing = getattr(gui.QPainter, "Antialiasing", None)
    if antialiasing is None:
        antialiasing = gui.QPainter.RenderHint.Antialiasing
    painter.setRenderHint(antialiasing, True)

    size = 16.0
    rtl = widget.layoutDirection() == _qt_enum(
        core, "RightToLeft", "LayoutDirection"
    )
    edge_inset = 3.0
    left = widget.width() - size - edge_inset if rtl else edge_inset
    indicator = core.QRectF(left, (widget.height() - size) / 2.0, size, size)
    if rtl:
        text_rect = core.QRectF(
            0, 0, max(0.0, widget.width() - size - 8.0), widget.height()
        )
    else:
        # Keep the stock Qt size hint viable: moving the indicator inward
        # trades only 3px of the visual gap rather than clipping label text.
        text_rect = core.QRectF(
            size + 8.0, 0, max(0.0, widget.width() - size - 8.0), widget.height()
        )

    primary = _semantic_color(widget, gui, "primary", "Highlight")
    background = _semantic_color(widget, gui, "background", "Window")
    foreground = _semantic_color(widget, gui, "foreground", "WindowText")
    accent = _semantic_color(widget, gui, "accent", "AlternateBase")
    ring = _semantic_color(widget, gui, "ring", "Highlight")
    enabled = widget.isEnabled()
    checked = widget.isChecked()
    partial = False
    if isinstance(widget, widgets.QCheckBox) and widget.isTristate():
        partial = widget.checkState() == _qt_enum(
            core, "PartiallyChecked", "CheckState"
        )
    if not enabled:
        primary = _with_alpha(gui, primary, 128)
        foreground = _with_alpha(gui, foreground, 128)

    no_brush = _qt_enum(core, "NoBrush", "BrushStyle")
    no_pen = _qt_enum(core, "NoPen", "PenStyle")
    if widget.hasFocus():
        painter.setBrush(no_brush)
        painter.setPen(gui.QPen(ring, 1))
        if component == "radio":
            painter.drawEllipse(indicator.adjusted(-1.5, -1.5, 1.5, 1.5))
        else:
            painter.drawRoundedRect(
                indicator.adjusted(-1.5, -1.5, 1.5, 1.5), 5, 5
            )

    painter.setPen(gui.QPen(primary, 1))
    if widget.underMouse() and not checked and not partial:
        painter.setBrush(accent)
    else:
        painter.setBrush(primary if (checked or partial) else background)
    if component == "radio":
        painter.drawEllipse(indicator)
        if checked:
            painter.setPen(no_pen)
            painter.setBrush(background)
            painter.drawEllipse(indicator.adjusted(4.5, 4.5, -4.5, -4.5))
    else:
        painter.drawRoundedRect(indicator, 3, 3)
        if checked or partial:
            mark = _semantic_color(
                widget, gui, "primaryForeground", "HighlightedText"
            )
            pen = gui.QPen(mark, 1.8)
            pen.setCapStyle(_qt_enum(core, "RoundCap", "PenCapStyle"))
            pen.setJoinStyle(_qt_enum(core, "RoundJoin", "PenJoinStyle"))
            painter.setPen(pen)
            if partial:
                y = indicator.center().y()
                painter.drawLine(
                    core.QPointF(indicator.left() + 4, y),
                    core.QPointF(indicator.right() - 4, y),
                )
            else:
                path = gui.QPainterPath()
                path.moveTo(indicator.left() + 3.5, indicator.center().y())
                path.lineTo(indicator.left() + 6.8, indicator.bottom() - 3.8)
                path.lineTo(indicator.right() - 3.2, indicator.top() + 3.8)
                painter.drawPath(path)

    painter.setPen(foreground)
    alignment = _qt_enum(core, "AlignVCenter", "AlignmentFlag")
    alignment |= _qt_enum(
        core, "AlignRight" if rtl else "AlignLeft", "AlignmentFlag"
    )
    painter.drawText(text_rect, int(alignment), widget.text())
    painter.end()
    return True


def _calendar_delegate_type() -> Any:
    global _CALENDAR_DELEGATE_TYPE
    if _CALENDAR_DELEGATE_TYPE is not None:
        return _CALENDAR_DELEGATE_TYPE

    core, gui, widgets = _qt.qt_modules()

    def style_state(name: str) -> Any:
        direct = getattr(widgets.QStyle, name, None)
        if direct is not None:
            return direct
        return getattr(widgets.QStyle.StateFlag, name)

    class NativeCalendarDelegate(widgets.QStyledItemDelegate):
        def paint(self, painter: Any, option: Any, index: Any) -> None:
            painter.save()
            antialiasing = getattr(gui.QPainter, "Antialiasing", None)
            if antialiasing is None:
                antialiasing = gui.QPainter.RenderHint.Antialiasing
            painter.setRenderHint(antialiasing, True)
            view = self.parent()
            foreground = _semantic_color(view, gui, "foreground", "WindowText")
            muted = _semantic_color(view, gui, "muted", "AlternateBase")
            muted_foreground = _semantic_color(
                view, gui, "mutedForeground", "WindowText"
            )
            primary = _semantic_color(view, gui, "primary", "Highlight")
            primary_foreground = _semantic_color(
                view, gui, "primaryForeground", "HighlightedText"
            )
            accent = _semantic_color(view, gui, "accent", "AlternateBase")
            text = str(index.data() or "")
            rect = core.QRectF(option.rect)
            center = _qt_enum(core, "AlignCenter", "AlignmentFlag")
            no_pen = _qt_enum(core, "NoPen", "PenStyle")
            if index.row() == 0:
                painter.setPen(no_pen)
                painter.setBrush(muted)
                painter.drawRect(rect)
                painter.setPen(muted_foreground)
                painter.drawText(rect, int(center), text)
                painter.restore()
                return

            side = min(32.0, rect.height() - 4.0)
            day_rect = core.QRectF(
                rect.center().x() - side / 2,
                rect.center().y() - side / 2,
                side,
                side,
            )
            selected = bool(option.state & style_state("State_Selected")) or (
                view.currentIndex() == index
            )
            hovered = bool(option.state & style_state("State_MouseOver"))
            enabled = bool(option.state & style_state("State_Enabled"))
            if selected:
                painter.setPen(no_pen)
                painter.setBrush(primary)
                painter.drawRoundedRect(day_rect, 6, 6)
                painter.setPen(primary_foreground)
            elif hovered:
                painter.setPen(no_pen)
                painter.setBrush(accent)
                painter.drawRoundedRect(day_rect, 6, 6)
                painter.setPen(foreground)
            else:
                painter.setPen(foreground if enabled else muted_foreground)
            painter.drawText(day_rect, int(center), text)
            painter.restore()

    _CALENDAR_DELEGATE_TYPE = NativeCalendarDelegate
    return _CALENDAR_DELEGATE_TYPE


def _set_mouse_transparent(widget: Any, core: Any) -> None:
    attribute = getattr(core.Qt, "WA_TransparentForMouseEvents", None)
    if attribute is None:
        attribute = core.Qt.WidgetAttribute.WA_TransparentForMouseEvents
    widget.setAttribute(attribute, True)


def _native_glyph_type() -> Any:
    global _NATIVE_GLYPH_TYPE
    if _NATIVE_GLYPH_TYPE is not None:
        return _NATIVE_GLYPH_TYPE

    core, gui, widgets = _qt.qt_modules()

    class NativeGlyph(widgets.QWidget):
        def __init__(self, direction: str, parent: Any) -> None:
            super().__init__(parent)
            self.direction = direction
            self.setObjectName(f"shadcnQtNativeGlyph{direction.title()}")
            self.setProperty(_PREFERENCE_PROPERTY, False)
            self.setProperty("nativeGlyph", True)
            _set_mouse_transparent(self, core)

        def _icon_path(self) -> Any:
            center = core.QRectF(self.rect()).center()
            vertical = -2.0 if self.direction == "up" else 2.0
            path = gui.QPainterPath()
            path.moveTo(center.x() - 4.0, center.y() - vertical)
            path.lineTo(center.x(), center.y() + vertical)
            path.lineTo(center.x() + 4.0, center.y() - vertical)
            return path

        def paintEvent(self, event: Any) -> None:
            del event
            painter = gui.QPainter(self)
            antialiasing = getattr(gui.QPainter, "Antialiasing", None)
            if antialiasing is None:
                antialiasing = gui.QPainter.RenderHint.Antialiasing
            painter.setRenderHint(antialiasing, True)
            color = _semantic_color(self, gui, "mutedForeground", "WindowText")
            if not self.isEnabled():
                color = _with_alpha(gui, color, 128)
            pen = gui.QPen(color, 1.5)
            pen.setCapStyle(_qt_enum(core, "RoundCap", "PenCapStyle"))
            pen.setJoinStyle(_qt_enum(core, "RoundJoin", "PenJoinStyle"))
            painter.setPen(pen)
            painter.drawPath(self._icon_path())

    _NATIVE_GLYPH_TYPE = NativeGlyph
    return _NATIVE_GLYPH_TYPE


def _layout_native_glyphs(widget: Any) -> None:
    state = getattr(widget, "_shadcn_qt_native_enhancements", None)
    if not state or not state.get("glyphs"):
        return
    glyphs = state["glyphs"]
    width = 28
    right = max(0, widget.width() - width)
    if len(glyphs) == 1:
        glyphs[0].setGeometry(right, 2, width - 2, max(1, widget.height() - 4))
        return
    top_height = max(1, widget.height() // 2)
    glyphs[0].setGeometry(right, 2, width - 2, max(1, top_height - 2))
    glyphs[1].setGeometry(
        right,
        top_height,
        width - 2,
        max(1, widget.height() - top_height - 2),
    )


def _add_native_glyphs(widget: Any, widgets: Any, state: Dict[str, Any]) -> None:
    directions: Tuple[str, ...]
    if isinstance(widget, widgets.QComboBox):
        directions = ("down",)
    elif isinstance(widget, widgets.QAbstractSpinBox):
        directions = ("up", "down")
    else:
        return
    glyphs = []
    glyph_type = _native_glyph_type()
    for direction in directions:
        glyph = glyph_type(direction, widget)
        glyph.show()
        glyphs.append(glyph)
    state["glyphs"] = glyphs
    _layout_native_glyphs(widget)


def _add_native_shadow(widget: Any, gui: Any, widgets: Any, state: Dict[str, Any]) -> None:
    eligible = isinstance(
        widget,
        (
            widgets.QPushButton,
            widgets.QLineEdit,
            widgets.QPlainTextEdit,
            widgets.QTextEdit,
            widgets.QKeySequenceEdit,
            widgets.QComboBox,
            widgets.QAbstractSpinBox,
        ),
    )
    if not eligible or widget.graphicsEffect() is not None:
        return
    if isinstance(widget, widgets.QPushButton) and widget.property("variant") in {
        "ghost",
        "link",
    }:
        return
    effect = widgets.QGraphicsDropShadowEffect(widget)
    is_button = isinstance(widget, widgets.QPushButton)
    effect.setBlurRadius(4.0 if is_button else 2.0)
    effect.setOffset(0.0, 1.0)
    effect.setColor(gui.QColor(0, 0, 0, 16 if is_button else 13))
    widget.setGraphicsEffect(effect)
    state["shadow"] = effect


def _sync_native_shadow(widget: Any, widgets: Any) -> None:
    state = getattr(widget, "_shadcn_qt_native_enhancements", None)
    if state is None:
        return
    shadow = state.get("shadow")
    wants_shadow = not (
        isinstance(widget, widgets.QPushButton)
        and widget.property("variant") in {"ghost", "link"}
    )
    if not wants_shadow and shadow is not None and widget.graphicsEffect() is shadow:
        widget.setGraphicsEffect(None)
        state.pop("shadow", None)
    elif wants_shadow and shadow is None:
        _, gui, _ = _qt.qt_modules()
        _add_native_shadow(widget, gui, widgets, state)


def _enhancement_filter_type() -> Any:
    global _ENHANCEMENT_FILTER_TYPE
    if _ENHANCEMENT_FILTER_TYPE is not None:
        return _ENHANCEMENT_FILTER_TYPE

    core, gui, widgets = _qt.qt_modules()
    paint = getattr(core.QEvent, "Paint", None)
    resize = getattr(core.QEvent, "Resize", None)
    show = getattr(core.QEvent, "Show", None)
    if paint is None:
        paint = core.QEvent.Type.Paint
        resize = core.QEvent.Type.Resize
        show = core.QEvent.Type.Show

    class NativeEnhancementFilter(core.QObject):
        def eventFilter(self, watched: Any, event: Any) -> bool:
            if not watched.property(_ADOPTED_PROPERTY):
                return False
            if event.type() in {resize, show}:
                _layout_native_glyphs(watched)
            elif event.type() == paint and isinstance(
                watched, (widgets.QCheckBox, widgets.QRadioButton)
            ):
                return _paint_native_choice(watched, core, gui, widgets)
            return False

    _ENHANCEMENT_FILTER_TYPE = NativeEnhancementFilter
    return _ENHANCEMENT_FILTER_TYPE


def _enhance_widget(widget: Any, widgets: Any) -> None:
    core, gui, _ = _qt.qt_modules()
    state = getattr(widget, "_shadcn_qt_native_enhancements", None)
    if state is None:
        state = {}
        widget._shadcn_qt_native_enhancements = state
        _add_native_glyphs(widget, widgets, state)
        _add_native_shadow(widget, gui, widgets, state)
        if isinstance(
            widget,
            (
                widgets.QCheckBox,
                widgets.QRadioButton,
                widgets.QComboBox,
                widgets.QAbstractSpinBox,
            ),
        ):
            event_filter = _enhancement_filter_type()(widget)
            widget.installEventFilter(event_filter)
            state["event_filter"] = event_filter

    if isinstance(widget, widgets.QCalendarWidget):
        view = widget.findChild(widgets.QTableView, "qt_calendar_calendarview")
        if view is None or "calendar" in state:
            return
        state["calendar"] = {
            "delegate": view.itemDelegate(),
            "grid": widget.isGridVisible(),
            "vertical_header": widget.verticalHeaderFormat(),
            "section_size": view.verticalHeader().defaultSectionSize(),
        }
        widget.setGridVisible(False)
        no_header = getattr(widgets.QCalendarWidget, "NoVerticalHeader", None)
        if no_header is None:
            no_header = widgets.QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        widget.setVerticalHeaderFormat(no_header)
        view.setMouseTracking(True)
        view.verticalHeader().setMinimumSectionSize(36)
        view.verticalHeader().setDefaultSectionSize(36)
        view.setItemDelegate(_calendar_delegate_type()(view))


def _restore_widget(widget: Any, widgets: Any) -> None:
    state = getattr(widget, "_shadcn_qt_native_enhancements", None)
    if state is None:
        return
    calendar = state.get("calendar")
    if calendar is not None and isinstance(widget, widgets.QCalendarWidget):
        view = widget.findChild(widgets.QTableView, "qt_calendar_calendarview")
        if view is not None:
            view.setItemDelegate(calendar["delegate"])
            view.verticalHeader().setDefaultSectionSize(calendar["section_size"])
        widget.setGridVisible(calendar["grid"])
        widget.setVerticalHeaderFormat(calendar["vertical_header"])
    for glyph in state.get("glyphs", ()):
        glyph.deleteLater()
    event_filter = state.get("event_filter")
    if event_filter is not None:
        widget.removeEventFilter(event_filter)
        event_filter.deleteLater()
    shadow = state.get("shadow")
    if shadow is not None and widget.graphicsEffect() is shadow:
        # Qt owns and deletes the old effect when it is detached.
        widget.setGraphicsEffect(None)
    delattr(widget, "_shadcn_qt_native_enhancements")


def _preference(widget: Any) -> Optional[bool]:
    value = widget.property(_PREFERENCE_PROPERTY)
    if value is None:
        return None
    return bool(value)


def _adopt_widget(widget: Any, widgets: Any, *, refresh: bool) -> bool:
    if widget.property(_ADOPTED_PROPERTY):
        return False
    preference = _preference(widget)
    if preference is False:
        return False
    if widget.property("shadcn_qt_component") not in (None, ""):
        return False
    if preference is not True and _is_internal_widget(widget, widgets):
        return False
    defaults = _native_defaults(widget, widgets)
    if defaults is None:
        return False

    added = []
    for name, value in defaults.items():
        if widget.property(name) is None:
            widget.setProperty(name, value)
            added.append(name)
    if not added:
        return False

    widget.setProperty(_ADOPTED_PROPERTY, True)
    widget.setProperty(_ADDED_PROPERTIES, ",".join(added))
    _enhance_widget(widget, widgets)
    if refresh:
        _refresh_style(widget)
    return True


def _clear_widget(widget: Any, widgets: Any, *, refresh: bool) -> bool:
    if not widget.property(_ADOPTED_PROPERTY):
        return False
    _restore_widget(widget, widgets)
    defaults = _native_defaults(widget, widgets) or {}
    names = str(widget.property(_ADDED_PROPERTIES) or "").split(",")
    # Clear the marker first so property-change events below are not mistaken
    # for user customization that needs a separate repolish.
    widget.setProperty(_ADOPTED_PROPERTY, None)
    for name in (item for item in names if item):
        if name in defaults and widget.property(name) == defaults[name]:
            widget.setProperty(name, None)
    widget.setProperty(_ADDED_PROPERTIES, None)
    if refresh:
        _refresh_style(widget)
    return True


def _widgets_below(root: Any, widgets: Any, *, recursive: bool) -> Iterable[Any]:
    if isinstance(root, widgets.QApplication):
        return tuple(root.allWidgets())
    if isinstance(root, widgets.QWidget):
        if not recursive:
            return (root,)
        return (root, *root.findChildren(widgets.QWidget))
    raise TypeError("root must be a QApplication or QWidget")


def adopt_native_widgets(
    root: Any,
    *,
    recursive: bool = True,
    refresh: bool = True,
) -> int:
    """Apply shadcn-qt default component properties below ``root``.

    Explicit ``shadcn_qt_component`` values and widgets with
    ``shadcn_qt_native_styling=False`` are left unchanged.  The return value is
    the number of widgets newly adopted.
    """

    _, _, widgets = _qt.qt_modules()
    return sum(
        _adopt_widget(widget, widgets, refresh=refresh)
        for widget in _widgets_below(root, widgets, recursive=recursive)
    )


def _event_property_name(event: Any) -> str:
    value = event.propertyName()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    data = getattr(value, "data", None)
    if callable(data):
        raw = data()
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace")
    return str(value)


def _adapter_type() -> Any:
    global _ADAPTER_TYPE
    if _ADAPTER_TYPE is not None:
        return _ADAPTER_TYPE

    core, _, widgets = _qt.qt_modules()
    polish = getattr(core.QEvent, "Polish", None)
    dynamic_change = getattr(core.QEvent, "DynamicPropertyChange", None)
    if polish is None:
        polish = core.QEvent.Type.Polish
        dynamic_change = core.QEvent.Type.DynamicPropertyChange

    class NativeWidgetStylingAdapter(core.QObject):
        def eventFilter(self, watched: Any, event: Any) -> bool:
            if not isinstance(watched, widgets.QWidget):
                return False
            if event.type() == polish:
                _adopt_widget(watched, widgets, refresh=False)
            elif (
                event.type() == dynamic_change
                and _event_property_name(event) == _PREFERENCE_PROPERTY
            ):
                if _preference(watched) is False:
                    _clear_widget(watched, widgets, refresh=True)
                else:
                    _adopt_widget(watched, widgets, refresh=True)
            elif (
                event.type() == dynamic_change
                and _event_property_name(event) in _STYLE_PROPERTIES
                and watched.property(_ADOPTED_PROPERTY)
            ):
                _sync_native_shadow(watched, widgets)
                _refresh_style(watched)
            return False

    _ADAPTER_TYPE = NativeWidgetStylingAdapter
    return _ADAPTER_TYPE


def enable_native_widget_styling(app: Any = None) -> Any:
    """Continuously adopt existing and future compatible native widgets."""

    _, _, widgets = _qt.qt_modules()
    if app is None:
        app = widgets.QApplication.instance()
    if app is None:
        raise RuntimeError("No QApplication instance; create QApplication first.")
    if not isinstance(app, widgets.QApplication):
        raise TypeError("app must be a QApplication")

    existing = getattr(app, _ADAPTER_ATTRIBUTE, None)
    if existing is not None:
        return existing
    adapter = _adapter_type()(app)
    app.installEventFilter(adapter)
    setattr(app, _ADAPTER_ATTRIBUTE, adapter)
    app.setProperty("shadcn_qt_native_styling_enabled", True)
    adopt_native_widgets(app)
    return adapter


def disable_native_widget_styling(app: Any = None, *, clear: bool = True) -> int:
    """Stop automatic adoption and optionally remove unchanged adapter defaults."""

    _, _, widgets = _qt.qt_modules()
    if app is None:
        app = widgets.QApplication.instance()
    if app is None:
        raise RuntimeError("No QApplication instance; create QApplication first.")
    if not isinstance(app, widgets.QApplication):
        raise TypeError("app must be a QApplication")

    adapter = getattr(app, _ADAPTER_ATTRIBUTE, None)
    if adapter is not None:
        app.removeEventFilter(adapter)
        delattr(app, _ADAPTER_ATTRIBUTE)
        adapter.deleteLater()
    app.setProperty("shadcn_qt_native_styling_enabled", False)

    cleared = 0
    if clear:
        for widget in tuple(app.allWidgets()):
            cleared += int(_clear_widget(widget, widgets, refresh=True))
    return cleared


__all__ = [
    "adopt_native_widgets",
    "disable_native_widget_styling",
    "enable_native_widget_styling",
]
