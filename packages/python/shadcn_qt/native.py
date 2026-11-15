"""Opt-in styling for existing native Qt widgets.

The adapter adds the same dynamic properties used by shadcn-qt subclasses to
compatible standard widgets.  It deliberately supplies only safe defaults;
semantic choices such as Card vs Alert or Checkbox vs Switch remain explicit.
"""

from __future__ import annotations

import weakref
from typing import Any, Dict, Iterable, Optional, Tuple

from shadcn_qt import _qt
from shadcn_qt._radius import format_radius, radius_pixels

_ADAPTER_ATTRIBUTE = "_shadcn_qt_native_widget_styling_adapter"
_ADOPTED_WIDGETS_ATTRIBUTE = "_shadcn_qt_native_adopted_widgets"
_ADOPTED_PROPERTY = "shadcn_qt_native_adopted"
_ADDED_PROPERTIES = "shadcn_qt_native_properties"
_ENHANCEMENTS_PROPERTY = "shadcn_qt_native_enhancements"
_PREFERENCE_PROPERTY = "shadcn_qt_native_styling"
_COMBO_POPUP_NAME = "shadcnQtNativeComboPopup"
_COMBO_POPUP_VIEW_NAME = "shadcnQtNativeComboPopupView"
_CHOICE_SHADOW_OFFSET_Y = 1.0
_CHOICE_SHADOW_LAYERS = ((1.0, 3), (0.5, 4), (0.0, 6))
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
_POPUP_POSITION_FILTER_TYPE: Optional[Any] = None
_TAB_PANE_FILTER_TYPE: Optional[Any] = None


class _EnhancementState(dict):
    """Keep Python-owned Qt wrappers opaque inside dynamic properties."""


def _refresh_style(widget: Any) -> None:
    style = widget.style()
    if style is not None:
        style.unpolish(widget)
        style.polish(widget)
    _, _, widgets = _qt.qt_modules()
    widgets.QWidget.update(widget)


def _track_adopted_widget(widget: Any) -> None:
    """Retain a non-owning record for deterministic adapter cleanup."""

    _, _, widgets = _qt.qt_modules()
    app = widgets.QApplication.instance()
    if app is None:
        return
    adopted = getattr(app, _ADOPTED_WIDGETS_ATTRIBUTE, None)
    if adopted is None:
        adopted = {}
        setattr(app, _ADOPTED_WIDGETS_ATTRIBUTE, adopted)
    adopted[id(widget)] = weakref.ref(widget)


def _forget_adopted_widget(widget: Any) -> None:
    _, _, widgets = _qt.qt_modules()
    app = widgets.QApplication.instance()
    adopted = (
        getattr(app, _ADOPTED_WIDGETS_ATTRIBUTE, None)
        if app is not None
        else None
    )
    if adopted is not None:
        adopted.pop(id(widget), None)


def _is_internal_widget(widget: Any, widgets: Any) -> bool:
    # Embedded editors are styled by their owning complex control. Applying a
    # second Input frame would produce a visible double border. Other Qt-owned
    # children are deliberately adopted so compatibility mode has no native
    # visual gaps.
    if isinstance(widget, widgets.QLineEdit):
        parent = widget.parentWidget()
        if isinstance(parent, (widgets.QComboBox, widgets.QAbstractSpinBox)):
            return True
    if isinstance(widget, widgets.QAbstractItemView):
        parent = widget.parentWidget()
        while parent is not None:
            if isinstance(parent, widgets.QComboBox):
                return True
            parent = parent.parentWidget()
    parent = widget.parentWidget()
    if isinstance(parent, widgets.QTabWidget) and isinstance(
        widget, (widgets.QTabBar, widgets.QStackedWidget)
    ):
        # A QTabWidget owns and styles its internal bar and page stack.
        # Adopting either child independently would apply a second container
        # frame over the shared Chrome tab-pane contract.
        return True
    if (
        isinstance(parent, widgets.QStackedWidget)
        and parent.objectName() == "qt_tabwidget_stackedwidget"
    ):
        tab_widget = parent.parentWidget()
        component = (
            tab_widget.property("shadcn_qt_component")
            if isinstance(tab_widget, widgets.QTabWidget)
            else None
        )
        if component in (None, "", "tab-pane"):
            # A document tab page is the pane surface itself. Adopting it as a
            # generic QWidget would repaint it with the window background and
            # visually disconnect it from the active tab title.
            return True
    if isinstance(parent, widgets.QTabBar) and isinstance(
        widget, widgets.QAbstractButton
    ):
        # Qt creates close and scroll buttons inside QTabBar. Treating them as
        # normal shadcn buttons changes their geometry and obscures tab labels.
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


def _enum_member(owner: Any, name: str, group: str) -> Any:
    """Resolve ``owner.name`` across binding enum spellings."""

    direct = getattr(owner, name, None)
    if direct is not None:
        return direct
    return getattr(getattr(owner, group, None), name, None)


def _frame_kind(widget: Any, widgets: Any) -> str:
    # PyQt5 exposes frame shapes as plain ints without a ``name`` attribute and
    # PyQt6 drops the short aliases, so resolve members through the binding
    # instead of reading the enum.
    shape = widget.frameShape()
    frame = widgets.QFrame
    for name in ("HLine", "VLine"):
        if shape == _enum_member(frame, name, "Shape"):
            return name.casefold()
    for name in ("Panel", "StyledPanel", "Box", "WinPanel"):
        if shape == _enum_member(frame, name, "Shape"):
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
        (widgets.QTabWidget, "tab-pane", {"nativeKind": "tab-widget"}),
        (widgets.QTabBar, "tab-pane-bar", {"nativeKind": "tab-bar"}),
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


def _semantic_radius(widget: Any, name: str, fallback: float) -> float:
    _, _, widgets = _qt.qt_modules()
    app = widgets.QApplication.instance()
    value = app.property(f"shadcn_qt_radius_{name}") if app is not None else None
    if value is None:
        return fallback
    try:
        return radius_pixels(str(value), name=f"radius[{name!r}]")
    except (TypeError, ValueError):
        return fallback


def _with_alpha(gui: Any, color: Any, alpha: int) -> Any:
    result = gui.QColor(color)
    result.setAlpha(max(0, min(255, int(alpha))))
    return result


def _paint_native_choice_shadow(
    painter: Any,
    indicator: Any,
    *,
    radio: bool,
    enabled: bool,
    corner_radius: float,
    core: Any,
    gui: Any,
) -> None:
    painter.save()
    painter.setPen(_qt_enum(core, "NoPen", "PenStyle"))
    for expansion, alpha in _CHOICE_SHADOW_LAYERS:
        if not enabled:
            alpha = round(alpha * 0.5)
        painter.setBrush(_with_alpha(gui, gui.QColor(0, 0, 0), alpha))
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
                corner_radius + expansion,
                corner_radius + expansion,
            )
    painter.restore()


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
    indicator_radius = min(
        _semantic_radius(widget, "sm", 4.0) * 0.75,
        indicator.height() / 2.0,
    )
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
            focus_radius = min(
                indicator_radius + 2.0,
                (indicator.height() + 3.0) / 2.0,
            )
            painter.drawRoundedRect(
                indicator.adjusted(-1.5, -1.5, 1.5, 1.5),
                focus_radius,
                focus_radius,
            )

    _paint_native_choice_shadow(
        painter,
        indicator,
        radio=component == "radio",
        enabled=enabled,
        corner_radius=indicator_radius,
        core=core,
        gui=gui,
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
        painter.drawRoundedRect(indicator, indicator_radius, indicator_radius)
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
            day_radius = min(
                _semantic_radius(view, "md", 6.0),
                day_rect.height() / 2.0,
            )
            if selected:
                painter.setPen(no_pen)
                painter.setBrush(primary)
                painter.drawRoundedRect(day_rect, day_radius, day_radius)
                painter.setPen(primary_foreground)
            elif hovered:
                painter.setPen(no_pen)
                painter.setBrush(accent)
                painter.drawRoundedRect(day_rect, day_radius, day_radius)
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


def _enhancement_state(widget: Any) -> Optional[Dict[str, Any]]:
    state = getattr(widget, "_shadcn_qt_native_enhancements", None)
    if state is not None:
        return state
    state = widget.property(_ENHANCEMENTS_PROPERTY)
    if isinstance(state, dict):
        widget._shadcn_qt_native_enhancements = state
        return state
    return None


def _store_enhancement_state(widget: Any, state: Dict[str, Any]) -> None:
    _track_adopted_widget(widget)
    widget._shadcn_qt_native_enhancements = state
    # Qt dynamic properties belong to the C++ object, so this state remains
    # reachable even when a binding creates a replacement Python wrapper while
    # constructing a complex subclass such as QFontComboBox.
    widget.setProperty(_ENHANCEMENTS_PROPERTY, state)


def _layout_native_glyphs(widget: Any) -> None:
    state = _enhancement_state(widget)
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


def _style_native_combo_popup(widget: Any) -> None:
    view = widget.view()
    popup = view.window()
    _, gui, _ = _qt.qt_modules()
    background = _semantic_color(widget, gui, "popover", "Base").name()
    foreground = _semantic_color(widget, gui, "popoverForeground", "Text").name()
    border = _semantic_color(widget, gui, "border", "Mid").name()
    accent = _semantic_color(widget, gui, "accent", "AlternateBase").name()
    accent_foreground = _semantic_color(
        widget, gui, "accentForeground", "Text"
    ).name()
    popup_radius = format_radius(_semantic_radius(widget, "md", 6.0))
    item_radius = format_radius(_semantic_radius(widget, "sm", 4.0))
    popup.setStyleSheet(
        f"#{_COMBO_POPUP_NAME} {{ background: {background}; "
        f"border: 1px solid {border}; border-radius: {popup_radius}; }} "
        f"#{_COMBO_POPUP_NAME} QAbstractItemView {{ background: transparent; "
        f"color: {foreground}; border: none; border-radius: 0; "
        "padding: 4px; outline: 0; } "
        f"#{_COMBO_POPUP_NAME} QAbstractItemView::item {{ min-height: 28px; "
        f"padding: 2px 8px; border: none; border-radius: {item_radius}; }} "
        f"#{_COMBO_POPUP_NAME} QAbstractItemView::item:selected {{ "
        f"background: {accent}; color: {accent_foreground}; }}"
    )
    popup.setFixedWidth(max(1, widget.width()))


def _position_native_popup_below(
    widget: Any,
    popup: Any,
    *,
    match_width: bool = False,
) -> None:
    core, _, _ = _qt.qt_modules()
    if match_width:
        popup.setFixedWidth(max(1, widget.width()))
    popup.move(widget.mapToGlobal(core.QPoint(0, widget.height())))


def _popup_position_filter_type() -> Any:
    global _POPUP_POSITION_FILTER_TYPE
    if _POPUP_POSITION_FILTER_TYPE is not None:
        return _POPUP_POSITION_FILTER_TYPE

    core, _, widgets = _qt.qt_modules()
    show = getattr(core.QEvent, "Show", None)
    if show is None:
        show = core.QEvent.Type.Show

    class NativePopupPositionFilter(core.QObject):
        def __init__(self, popup: Any, *, match_width: bool) -> None:
            super().__init__(popup)
            self._match_width = match_width

        def eventFilter(self, watched: Any, event: Any) -> bool:
            if event.type() == show:
                anchor = watched.parentWidget()
                if anchor is not None:
                    if isinstance(anchor, widgets.QComboBox):
                        state = _enhancement_state(anchor)
                        if state is not None:
                            _ensure_native_combo_popup_delegate(anchor, state)
                    _position_native_popup_below(
                        anchor,
                        watched,
                        match_width=self._match_width,
                    )
            return False

    _POPUP_POSITION_FILTER_TYPE = NativePopupPositionFilter
    return _POPUP_POSITION_FILTER_TYPE


def _mark_native_combo_popup(
    widget: Any,
    state: Dict[str, Any],
    *,
    defer_font_delegate: bool = True,
) -> None:
    from shadcn_qt.widgets._style import install_combo_popup_delegate

    _, _, widgets = _qt.qt_modules()
    view = widget.view()
    popup = view.window()
    state["combo_popup"] = {
        "delegate": view.itemDelegate(),
        "popup": popup,
        "popup_maximum_width": popup.maximumWidth(),
        "popup_minimum_width": popup.minimumWidth(),
        "popup_name": popup.objectName(),
        "popup_stylesheet": popup.styleSheet(),
        "view": view,
        "view_name": view.objectName(),
    }
    # QFontComboBox is polished while its constructor is still replacing its
    # internal model and delegate on some bindings. Defer the proxy until the
    # control or popup is shown, when those internals are stable.
    if not defer_font_delegate or not isinstance(widget, widgets.QFontComboBox):
        install_combo_popup_delegate(widget)
    popup.setObjectName(_COMBO_POPUP_NAME)
    view.setObjectName(_COMBO_POPUP_VIEW_NAME)
    position_filter = _popup_position_filter_type()(popup, match_width=True)
    popup.installEventFilter(position_filter)
    state["combo_popup"]["position_filter"] = position_filter
    _style_native_combo_popup(widget)


def _ensure_native_combo_popup_delegate(
    widget: Any,
    state: Dict[str, Any],
) -> None:
    """Re-wrap a popup delegate replaced after native adoption."""

    combo_popup = state.get("combo_popup")
    if combo_popup is None:
        return
    view = widget.view()
    original_view = combo_popup["view"]
    try:
        same_view = view is original_view or view == original_view
    except RuntimeError:
        same_view = False
    if not same_view:
        _mark_native_combo_popup(
            widget,
            state,
            defer_font_delegate=False,
        )
        return
    current = view.itemDelegate()
    from shadcn_qt.widgets._style import ComboPopupItemDelegate

    if isinstance(current, ComboPopupItemDelegate):
        return

    from shadcn_qt.widgets._style import install_combo_popup_delegate

    install_combo_popup_delegate(widget)
    combo_popup["delegate"] = current


def _resync_native_combo_enhancements(
    widget: Any,
    state: Dict[str, Any],
) -> None:
    """Repair filters or delegates replaced during complex construction."""

    event_filter = state.get("event_filter")
    if event_filter is not None:
        widget.removeEventFilter(event_filter)
        widget.installEventFilter(event_filter)
    _ensure_native_combo_popup_delegate(widget, state)
    combo_popup = state.get("combo_popup")
    if combo_popup is not None:
        position_filter = combo_popup.get("position_filter")
        if position_filter is not None:
            combo_popup["popup"].removeEventFilter(position_filter)
            combo_popup["popup"].installEventFilter(position_filter)
    _style_native_combo_popup(widget)
    _store_enhancement_state(widget, state)


def _mark_native_calendar_popup(widget: Any, state: Dict[str, Any]) -> None:
    if "calendar_popup" in state or not widget.calendarPopup():
        return
    calendar = widget.calendarWidget()
    if calendar is None:
        return
    popup = calendar.window()
    position_filter = _popup_position_filter_type()(popup, match_width=False)
    popup.installEventFilter(position_filter)
    state["calendar_popup"] = {
        "popup": popup,
        "position_filter": position_filter,
    }


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


def _tab_pane_filter_type() -> Any:
    global _TAB_PANE_FILTER_TYPE
    if _TAB_PANE_FILTER_TYPE is not None:
        return _TAB_PANE_FILTER_TYPE

    core, _, _ = _qt.qt_modules()
    child_added = getattr(core.QEvent, "ChildAdded", None)
    layout_request = getattr(core.QEvent, "LayoutRequest", None)
    paint = getattr(core.QEvent, "Paint", None)
    show = getattr(core.QEvent, "Show", None)
    if child_added is None:
        child_added = core.QEvent.Type.ChildAdded
        layout_request = core.QEvent.Type.LayoutRequest
        paint = core.QEvent.Type.Paint
        show = core.QEvent.Type.Show

    class NativeTabPaneFilter(core.QObject):
        def __init__(self, tab_widget: Any) -> None:
            super().__init__(tab_widget)
            self._tab_widget = tab_widget
            self._pending = False

        def _sync(self) -> None:
            self._pending = False
            try:
                if not self._tab_widget.property(_ADOPTED_PROPERTY):
                    return
                from shadcn_qt.widgets._tab_pane import sync_tab_close_buttons

                sync_tab_close_buttons(self._tab_widget)
            except RuntimeError:
                pass

        def eventFilter(self, watched: Any, event: Any) -> bool:
            if event.type() == paint and watched is self._tab_widget.tabBar():
                from shadcn_qt.widgets._tab_pane import paint_tab_bar

                paint_tab_bar(watched)
                return True
            if event.type() in {child_added, layout_request, show} and not self._pending:
                self._pending = True
                core.QTimer.singleShot(0, self._sync)
            return False

    _TAB_PANE_FILTER_TYPE = NativeTabPaneFilter
    return _TAB_PANE_FILTER_TYPE


def _enhance_native_tab_pane(widget: Any, state: Dict[str, Any]) -> None:
    if "tab_pane" in state:
        return
    core, _, _ = _qt.qt_modules()
    from shadcn_qt.widgets._tab_pane import (
        prepare_tab_pane,
        sync_tab_close_buttons,
    )

    bar = widget.tabBar()
    styled_background = getattr(core.Qt, "WA_StyledBackground", None)
    if styled_background is None:
        styled_background = core.Qt.WidgetAttribute.WA_StyledBackground
    mac_focus_rect = getattr(core.Qt, "WA_MacShowFocusRect", None)
    if mac_focus_rect is None:
        mac_focus_rect = getattr(
            core.Qt.WidgetAttribute,
            "WA_MacShowFocusRect",
            None,
        )
    event_filter = _tab_pane_filter_type()(widget)
    state["tab_pane"] = {
        "bar": bar,
        "draw_base": bar.drawBase(),
        "elide_mode": bar.elideMode(),
        "event_filter": event_filter,
        "mouse_tracking": bar.hasMouseTracking(),
        "styled_background": bar.testAttribute(styled_background),
        "styled_background_attribute": styled_background,
        "mac_focus_rect": (
            bar.testAttribute(mac_focus_rect)
            if mac_focus_rect is not None
            else None
        ),
        "mac_focus_rect_attribute": mac_focus_rect,
        "uses_scroll_buttons": bar.usesScrollButtons(),
    }
    frame_overlay = prepare_tab_pane(widget)
    state["tab_pane"]["frame_overlay"] = frame_overlay
    widget.installEventFilter(event_filter)
    bar.installEventFilter(event_filter)
    sync_tab_close_buttons(widget)


def _sync_native_shadow(widget: Any, widgets: Any) -> None:
    state = _enhancement_state(widget)
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
    _store_enhancement_state(widget, state)


def _margin_values(target: Any) -> Tuple[int, int, int, int]:
    margins = target.contentsMargins()
    return (
        margins.left(),
        margins.top(),
        margins.right(),
        margins.bottom(),
    )


def _message_box_has_icon(widget: Any, widgets: Any) -> bool:
    no_icon = getattr(widgets.QMessageBox, "NoIcon", None)
    if no_icon is None:
        no_icon = widgets.QMessageBox.Icon.NoIcon
    return widget.icon() != no_icon


def _sync_native_message_box(
    widget: Any,
    widgets: Any,
    message_box: Dict[str, Any],
) -> None:
    layout = widget.layout()
    if not isinstance(layout, widgets.QGridLayout):
        return
    button_box = widget.findChild(
        widgets.QDialogButtonBox,
        "qt_msgbox_buttonbox",
    )
    button_layout = button_box.layout() if button_box is not None else None
    if button_layout is None:
        return
    changed = False
    applied_margins = message_box["applied_margins"]
    if _margin_values(widget) != applied_margins:
        widget.setContentsMargins(*applied_margins)
        changed = True
    applied_layout_margins = message_box["applied_layout_margins"]
    if _margin_values(layout) != applied_layout_margins:
        layout.setContentsMargins(*applied_layout_margins)
        changed = True
    applied_vertical_spacing = message_box["applied_vertical_spacing"]
    if layout.verticalSpacing() != applied_vertical_spacing:
        layout.setVerticalSpacing(applied_vertical_spacing)
        changed = True

    has_icon = _message_box_has_icon(widget, widgets)
    labels = []
    for (
        object_name,
        _original_alignment,
        applied_alignment,
    ) in message_box["labels"]:
        label = widget.findChild(widgets.QLabel, object_name)
        if label is not None:
            labels.append(label)
            if label.alignment() != applied_alignment:
                label.setAlignment(applied_alignment)
                changed = True

    button_margins = message_box["applied_button_margins"]
    if _margin_values(button_layout) != button_margins:
        button_layout.setContentsMargins(*button_margins)
        changed = True

    if changed:
        layout.invalidate()
        button_layout.invalidate()
        layout.activate()
        button_layout.activate()
        widget.updateGeometry()
    if not has_icon:
        contents = widget.contentsRect()
        for label in labels:
            geometry = label.geometry()
            geometry.setLeft(contents.left())
            geometry.setRight(contents.right())
            if label.geometry() != geometry:
                label.setGeometry(geometry)


def _enhance_native_message_box(
    widget: Any,
    core: Any,
    widgets: Any,
    state: Dict[str, Any],
) -> None:
    if "message_box" in state:
        return
    layout = widget.layout()
    if not isinstance(layout, widgets.QGridLayout):
        return
    title = widget.findChild(widgets.QLabel, "qt_msgbox_label")
    information = widget.findChild(
        widgets.QLabel,
        "qt_msgbox_informativelabel",
    )
    button_box = widget.findChild(
        widgets.QDialogButtonBox,
        "qt_msgbox_buttonbox",
    )
    if title is None or information is None or button_box is None:
        return
    button_layout = button_box.layout()
    if button_layout is None:
        return

    horizontal_center = _qt_enum(core, "AlignHCenter", "AlignmentFlag")
    align_left = _qt_enum(core, "AlignLeft", "AlignmentFlag")
    vertical_center = _qt_enum(core, "AlignVCenter", "AlignmentFlag")
    title_alignment = horizontal_center | vertical_center
    information_alignment = align_left | vertical_center
    message_box = {
        "applied_button_margins": (0, 16, 0, 0),
        "applied_layout_margins": (0, 0, 0, 0),
        "applied_margins": (24, 24, 24, 24),
        "applied_vertical_spacing": 8,
        "button_margins": _margin_values(button_layout),
        "contents_margins": _margin_values(widget),
        "layout_margins": _margin_values(layout),
        "vertical_spacing": layout.verticalSpacing(),
        "labels": (
            ("qt_msgbox_label", title.alignment(), title_alignment),
            (
                "qt_msgbox_informativelabel",
                information.alignment(),
                information_alignment,
            ),
        ),
    }
    state["message_box"] = message_box
    _sync_native_message_box(widget, widgets, message_box)


def _enhancement_filter_type() -> Any:
    global _ENHANCEMENT_FILTER_TYPE
    if _ENHANCEMENT_FILTER_TYPE is not None:
        return _ENHANCEMENT_FILTER_TYPE

    core, gui, widgets = _qt.qt_modules()
    paint = getattr(core.QEvent, "Paint", None)
    palette_change = getattr(core.QEvent, "PaletteChange", None)
    mouse_press = getattr(core.QEvent, "MouseButtonPress", None)
    mouse_release = getattr(core.QEvent, "MouseButtonRelease", None)
    layout_request = getattr(core.QEvent, "LayoutRequest", None)
    resize = getattr(core.QEvent, "Resize", None)
    show = getattr(core.QEvent, "Show", None)
    if paint is None:
        paint = core.QEvent.Type.Paint
        resize = core.QEvent.Type.Resize
        show = core.QEvent.Type.Show
    if layout_request is None:
        layout_request = core.QEvent.Type.LayoutRequest
    if palette_change is None:
        palette_change = core.QEvent.Type.PaletteChange
    if mouse_press is None:
        mouse_press = core.QEvent.Type.MouseButtonPress
        mouse_release = core.QEvent.Type.MouseButtonRelease

    class NativeEnhancementFilter(core.QObject):
        def eventFilter(self, watched: Any, event: Any) -> bool:
            if not watched.property(_ADOPTED_PROPERTY):
                return False
            event_type = event.type()
            if isinstance(watched, widgets.QMessageBox) and event_type in {
                layout_request,
                paint,
                resize,
                show,
            }:
                state = _enhancement_state(watched)
                message_box = state.get("message_box") if state is not None else None
                if state is not None:
                    try:
                        if message_box is None:
                            _enhance_native_message_box(
                                watched,
                                core,
                                widgets,
                                state,
                            )
                            _store_enhancement_state(watched, state)
                        else:
                            _sync_native_message_box(
                                watched,
                                widgets,
                                message_box,
                            )
                    except RuntimeError:
                        pass
            if isinstance(watched, widgets.QComboBox) and event_type in {
                mouse_press,
                mouse_release,
            }:
                left_button = _qt_enum(core, "LeftButton", "MouseButton")
                if event_type == mouse_press and event.button() == left_button:
                    watched._shadcn_qt_combo_click_pending = True
                    watched.setFocus()
                    event.accept()
                    return True
                pending = getattr(
                    watched,
                    "_shadcn_qt_combo_click_pending",
                    False,
                )
                if event_type == mouse_release and pending:
                    watched._shadcn_qt_combo_click_pending = False
                    if event.button() == left_button:
                        position = getattr(event, "position", None)
                        point = (
                            position().toPoint()
                            if callable(position)
                            else event.pos()
                        )
                        if watched.rect().contains(point):
                            state = _enhancement_state(watched)
                            if state is not None:
                                _ensure_native_combo_popup_delegate(
                                    watched,
                                    state,
                                )
                            watched.showPopup()
                    event.accept()
                    return True
            if event_type in {resize, show}:
                _layout_native_glyphs(watched)
                if isinstance(watched, widgets.QComboBox):
                    state = _enhancement_state(watched)
                    if state is not None:
                        _ensure_native_combo_popup_delegate(watched, state)
                    _style_native_combo_popup(watched)
            elif event_type == palette_change and isinstance(
                watched, widgets.QComboBox
            ):
                _style_native_combo_popup(watched)
            elif event_type == paint and isinstance(
                watched, (widgets.QCheckBox, widgets.QRadioButton)
            ):
                return _paint_native_choice(watched, core, gui, widgets)
            return False

    _ENHANCEMENT_FILTER_TYPE = NativeEnhancementFilter
    return _ENHANCEMENT_FILTER_TYPE


def _enhance_widget(widget: Any, widgets: Any) -> None:
    core, gui, _ = _qt.qt_modules()
    state = _enhancement_state(widget)
    if state is None:
        state = _EnhancementState()
        widget._shadcn_qt_native_enhancements = state
        _add_native_glyphs(widget, widgets, state)
        if isinstance(widget, widgets.QComboBox):
            _mark_native_combo_popup(widget, state)
        if isinstance(widget, widgets.QDateTimeEdit):
            _mark_native_calendar_popup(widget, state)
        if isinstance(widget, widgets.QTabWidget):
            _enhance_native_tab_pane(widget, state)
        if isinstance(widget, widgets.QMessageBox):
            _enhance_native_message_box(widget, core, widgets, state)
        _add_native_shadow(widget, gui, widgets, state)
        if isinstance(
            widget,
            (
                widgets.QCheckBox,
                widgets.QRadioButton,
                widgets.QComboBox,
                widgets.QAbstractSpinBox,
                widgets.QMessageBox,
            ),
        ):
            event_filter = _enhancement_filter_type()(widget)
            widget.installEventFilter(event_filter)
            state["event_filter"] = event_filter

    if isinstance(widget, widgets.QCalendarWidget):
        view = widget.findChild(widgets.QTableView, "qt_calendar_calendarview")
        if view is not None and "calendar" not in state:
            state["calendar"] = {
                "delegate": view.itemDelegate(),
                "grid": widget.isGridVisible(),
                "vertical_header": widget.verticalHeaderFormat(),
                "section_size": view.verticalHeader().defaultSectionSize(),
            }
            widget.setGridVisible(False)
            no_header = getattr(widgets.QCalendarWidget, "NoVerticalHeader", None)
            if no_header is None:
                no_header = (
                    widgets.QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
                )
            widget.setVerticalHeaderFormat(no_header)
            view.setMouseTracking(True)
            view.verticalHeader().setMinimumSectionSize(36)
            view.verticalHeader().setDefaultSectionSize(36)
            applied_delegate = _calendar_delegate_type()(view)
            # Qt does not take ownership of an item delegate. Keep the proxy
            # reachable from the enhancement state, otherwise PyQt releases it
            # as soon as this function returns and the view falls back to a
            # plain QStyledItemDelegate.
            state["calendar"]["applied_delegate"] = applied_delegate
            view.setItemDelegate(applied_delegate)
    _store_enhancement_state(widget, state)


def _restore_widget(widget: Any, widgets: Any) -> None:
    state = _enhancement_state(widget)
    if state is None:
        return
    event_filter = state.get("event_filter")
    if event_filter is not None:
        widget.removeEventFilter(event_filter)
        event_filter.deleteLater()
    message_box = state.get("message_box")
    if message_box is not None and isinstance(widget, widgets.QMessageBox):
        try:
            if _margin_values(widget) == message_box["applied_margins"]:
                widget.setContentsMargins(*message_box["contents_margins"])
            for (
                object_name,
                original_alignment,
                applied_alignment,
            ) in message_box["labels"]:
                label = widget.findChild(widgets.QLabel, object_name)
                if (
                    label is not None
                    and label.alignment() == applied_alignment
                ):
                    label.setAlignment(original_alignment)
            layout = widget.layout()
            if (
                _margin_values(layout)
                == message_box["applied_layout_margins"]
            ):
                layout.setContentsMargins(*message_box["layout_margins"])
            if (
                layout.verticalSpacing()
                == message_box["applied_vertical_spacing"]
            ):
                layout.setVerticalSpacing(message_box["vertical_spacing"])
            button_box = widget.findChild(
                widgets.QDialogButtonBox,
                "qt_msgbox_buttonbox",
            )
            button_layout = button_box.layout() if button_box is not None else None
            if button_layout is not None:
                if (
                    _margin_values(button_layout)
                    == message_box["applied_button_margins"]
                ):
                    button_layout.setContentsMargins(
                        *message_box["button_margins"]
                    )
                button_layout.invalidate()
            layout.invalidate()
            layout.activate()
            widget.updateGeometry()
        except RuntimeError:
            pass
    calendar = state.get("calendar")
    if calendar is not None and isinstance(widget, widgets.QCalendarWidget):
        view = widget.findChild(widgets.QTableView, "qt_calendar_calendarview")
        if view is not None:
            view.setItemDelegate(calendar["delegate"])
            view.verticalHeader().setDefaultSectionSize(calendar["section_size"])
        calendar.pop("applied_delegate", None)
        widget.setGridVisible(calendar["grid"])
        widget.setVerticalHeaderFormat(calendar["vertical_header"])
    calendar_popup = state.get("calendar_popup")
    if calendar_popup is not None:
        try:
            popup = calendar_popup["popup"]
            position_filter = calendar_popup["position_filter"]
            popup.removeEventFilter(position_filter)
            position_filter.deleteLater()
        except RuntimeError:
            pass
    combo_popup = state.get("combo_popup")
    if combo_popup is not None:
        try:
            position_filter = combo_popup.get("position_filter")
            if position_filter is not None:
                combo_popup["popup"].removeEventFilter(position_filter)
                position_filter.deleteLater()
            combo_popup["popup"].setObjectName(combo_popup["popup_name"])
            combo_popup["popup"].setStyleSheet(combo_popup["popup_stylesheet"])
            combo_popup["popup"].setMinimumWidth(
                combo_popup["popup_minimum_width"]
            )
            combo_popup["popup"].setMaximumWidth(
                combo_popup["popup_maximum_width"]
            )
            combo_popup["view"].setObjectName(combo_popup["view_name"])
            installed = getattr(
                widget,
                "_shadcn_qt_combo_popup_delegate",
                None,
            )
            replacement = installed[1] if installed is not None else getattr(
                combo_popup["view"],
                "_shadcn_qt_combo_popup_delegate",
                None,
            )
            if replacement is not None:
                from shadcn_qt.widgets._style import (
                    restore_combo_popup_delegate,
                )

                restore_combo_popup_delegate(
                    widget,
                    combo_popup["view"],
                    replacement,
                    combo_popup["delegate"],
                )
        except RuntimeError:
            pass
    tab_pane = state.get("tab_pane")
    if tab_pane is not None and isinstance(widget, widgets.QTabWidget):
        try:
            bar = tab_pane["bar"]
            event_filter = tab_pane["event_filter"]
            frame_overlay = tab_pane.get("frame_overlay")
            widget.removeEventFilter(event_filter)
            bar.removeEventFilter(event_filter)
            event_filter.deleteLater()
            if frame_overlay is not None:
                widget.removeEventFilter(frame_overlay)
                frame_overlay.hide()
                frame_overlay.deleteLater()
                if (
                    getattr(
                        widget,
                        "_shadcn_qt_tab_pane_frame_overlay",
                        None,
                    )
                    is frame_overlay
                ):
                    delattr(widget, "_shadcn_qt_tab_pane_frame_overlay")
            bar.setDrawBase(tab_pane["draw_base"])
            bar.setElideMode(tab_pane["elide_mode"])
            bar.setMouseTracking(tab_pane["mouse_tracking"])
            bar.setUsesScrollButtons(tab_pane["uses_scroll_buttons"])
            bar.setAttribute(
                tab_pane["styled_background_attribute"],
                tab_pane["styled_background"],
            )
            mac_focus_rect = tab_pane.get("mac_focus_rect_attribute")
            if mac_focus_rect is not None:
                bar.setAttribute(
                    mac_focus_rect,
                    tab_pane["mac_focus_rect"],
                )
            if widget.tabsClosable():
                widget.setTabsClosable(False)
                widget.setTabsClosable(True)
        except RuntimeError:
            pass
    for glyph in state.get("glyphs", ()):
        glyph.deleteLater()
    shadow = state.get("shadow")
    if shadow is not None and widget.graphicsEffect() is shadow:
        # Qt owns and deletes the old effect when it is detached.
        widget.setGraphicsEffect(None)
    if hasattr(widget, "_shadcn_qt_combo_click_pending"):
        delattr(widget, "_shadcn_qt_combo_click_pending")
    widget.setProperty(_ENHANCEMENTS_PROPERTY, None)
    if hasattr(widget, "_shadcn_qt_native_enhancements"):
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
    component = widget.property("shadcn_qt_component")
    explicit_tab_pane = (
        isinstance(widget, widgets.QTabWidget) and component == "tab-pane"
    )
    if component not in (None, "") and not explicit_tab_pane:
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
    if not added and not explicit_tab_pane:
        return False

    widget.setProperty(_ADOPTED_PROPERTY, True)
    widget.setProperty(_ADDED_PROPERTIES, ",".join(added))
    _track_adopted_widget(widget)
    _enhance_widget(widget, widgets)
    if refresh:
        _refresh_style(widget)
    return True


def _clear_widget(widget: Any, widgets: Any, *, refresh: bool) -> bool:
    try:
        adopted = widget.property(_ADOPTED_PROPERTY)
    except RuntimeError:
        _forget_adopted_widget(widget)
        return False
    if not adopted:
        _forget_adopted_widget(widget)
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
    _forget_adopted_widget(widget)
    return True


def _widgets_below(root: Any, widgets: Any, *, recursive: bool) -> Iterable[Any]:
    if isinstance(root, widgets.QApplication):
        # QApplication.allWidgets() can expose wrappers whose C++ objects are
        # already pending deferred deletion. Shiboken may segfault while
        # materializing that global list after popup-heavy test/application
        # activity. Every live widget is either a top-level widget or one of
        # its descendants, so build the same practical snapshot from stable
        # ownership trees instead.
        snapshot = []
        for top_level in tuple(root.topLevelWidgets()):
            snapshot.append(top_level)
            snapshot.extend(top_level.findChildren(widgets.QWidget))
        return tuple(snapshot)
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
    show = getattr(core.QEvent, "Show", None)
    if polish is None:
        polish = core.QEvent.Type.Polish
        dynamic_change = core.QEvent.Type.DynamicPropertyChange
    if show is None:
        show = core.QEvent.Type.Show

    class NativeWidgetStylingAdapter(core.QObject):
        def eventFilter(self, watched: Any, event: Any) -> bool:
            if not isinstance(watched, widgets.QWidget):
                return False
            if event.type() == polish:
                _adopt_widget(watched, widgets, refresh=False)
                parent = watched.parentWidget()
                if (
                    isinstance(parent, widgets.QDateTimeEdit)
                    and parent.property(_ADOPTED_PROPERTY)
                ):
                    state = _enhancement_state(parent)
                    if state is not None:
                        _mark_native_calendar_popup(parent, state)
                        _store_enhancement_state(parent, state)
            elif (
                event.type() == show
                and isinstance(watched, widgets.QComboBox)
                and watched.property(_ADOPTED_PROPERTY)
            ):
                state = _enhancement_state(watched)
                if state is not None:
                    _resync_native_combo_enhancements(watched, state)
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
        adopted = getattr(app, _ADOPTED_WIDGETS_ATTRIBUTE, ())
        references = adopted.values() if isinstance(adopted, dict) else ()
        for reference in tuple(references):
            widget = reference()
            if widget is None:
                continue
            cleared += int(_clear_widget(widget, widgets, refresh=True))
        if hasattr(app, _ADOPTED_WIDGETS_ATTRIBUTE):
            delattr(app, _ADOPTED_WIDGETS_ATTRIBUTE)
    return cleared


__all__ = [
    "adopt_native_widgets",
    "disable_native_widget_styling",
    "enable_native_widget_styling",
]
